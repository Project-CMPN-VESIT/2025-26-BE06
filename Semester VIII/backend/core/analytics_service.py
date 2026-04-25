import pandas as pd
import numpy as np
from pathlib import Path
import re
from collections import Counter

class AnalyticsService:
    def __init__(self, data_dir="data/scraped"):
        self.data_dir = Path(data_dir)
    
    def get_latest_csv_files(self):
        """Get the most recent CSV files from both sources"""
        acres_files = sorted(self.data_dir.glob("99acres_processed_*.csv"), reverse=True)
        housing_files = sorted(self.data_dir.glob("housing_processed_*.csv"), reverse=True)
        
        return {
            "99acres": acres_files[0] if acres_files else None,
            "housing": housing_files[0] if housing_files else None
        }
    
    def parse_price(self, price_str):
        """Convert price string to numeric value in Crores"""
        if not price_str or price_str == "N/A":
            return None
        
        # Remove currency symbol and extra spaces
        price_str = str(price_str).replace('₹', '').replace(',', '').strip()
        
        # Handle Crores
        if 'Cr' in price_str or 'C' in price_str:
            match = re.search(r'([\d.]+)', price_str)
            if match:
                return float(match.group(1))
        
        # Handle Lakhs
        if 'Lac' in price_str or 'L' in price_str:
            match = re.search(r'([\d.]+)', price_str)
            if match:
                return float(match.group(1)) / 100  # Convert to Crores
        
        # Handle raw numbers (assume in lakhs for small numbers, crores for large)
        try:
            value = float(price_str)
            if value < 100:  # Likely in Crores
                return value
            elif value < 10000:  # Likely in Lakhs
                return value / 100
            else:  # Very large number, treat as rupees
                return value / 10000000
        except:
            return None
    
    def get_dashboard_analytics(self):
        """Generate comprehensive analytics for the dashboard"""
        files = self.get_latest_csv_files()
        
        # Load 99acres data
        df_99acres = None
        if files["99acres"]:
            try:
                df_99acres = pd.read_csv(files["99acres"])
            except Exception as e:
                print(f"Error loading 99acres data: {e}")
        
        # Load housing data
        df_housing = None
        if files["housing"]:
            try:
                df_housing = pd.read_csv(files["housing"])
            except Exception as e:
                print(f"Error loading housing data: {e}")
        
        if df_99acres is None and df_housing is None:
            return None
        
        # Primary analysis on 99acres data
        analytics = {}
        
        if df_99acres is not None and len(df_99acres) > 0:
            # Clean data
            df = df_99acres.copy()
            
            # Total properties
            analytics['total_properties'] = len(df)
            
            # BHK Distribution
            bhk_counts = df['bhk'].value_counts().head(6)
            analytics['bhk_distribution'] = [
                {"name": str(bhk), "count": int(count)} 
                for bhk, count in bhk_counts.items()
            ]
            
            # Top Localities
            locality_counts = df['locality'].value_counts().head(10)
            analytics['top_localities'] = [
                {"locality": str(loc)[:30], "count": int(count)} 
                for loc, count in locality_counts.items()
            ]
            
            # Price Distribution
            df['price_numeric'] = df['price'].apply(self.parse_price)
            price_ranges = [
                ("< 1 Cr", 0, 1),
                ("1-2 Cr", 1, 2),
                ("2-3 Cr", 2, 3),
                ("3-5 Cr", 3, 5),
                ("5-10 Cr", 5, 10),
                ("> 10 Cr", 10, float('inf'))
            ]
            
            price_distribution = []
            for label, min_val, max_val in price_ranges:
                count = len(df[(df['price_numeric'] >= min_val) & (df['price_numeric'] < max_val)])
                if count > 0:
                    price_distribution.append({"range": label, "count": count})
            
            analytics['price_distribution'] = price_distribution
            
            # Average price
            avg_price = df['price_numeric'].mean()
            analytics['average_price'] = f"{avg_price:.2f}" if not pd.isna(avg_price) else "N/A"
            
            # Status Distribution
            status_counts = df['status'].value_counts()
            analytics['status_distribution'] = [
                {"name": str(status), "count": int(count)} 
                for status, count in status_counts.items()
            ]
            
            # Under construction percentage
            total = len(df[df['status'] != 'N/A'])
            under_construction = len(df[df['status'] == 'Under Construction'])
            analytics['under_construction_percentage'] = int((under_construction / total * 100)) if total > 0 else 0
            
            # Furnishing Distribution
            furnishing_counts = df['furnishing'].value_counts()
            analytics['furnishing_distribution'] = [
                {"type": str(furn), "count": int(count)} 
                for furn, count in furnishing_counts.items() if furn != 'N/A'
            ]
            
            # RERA Distribution
            rera_yes = len(df[df['rera_flag'] == 'Yes'])
            rera_no = len(df[df['rera_flag'] == 'No'])
            analytics['rera_distribution'] = [
                {"name": "RERA Verified", "count": rera_yes},
                {"name": "Not Verified", "count": rera_no}
            ]
            analytics['rera_percentage'] = int((rera_yes / (rera_yes + rera_no) * 100)) if (rera_yes + rera_no) > 0 else 0
        
        # Add Housing.com insights if available
        if df_housing is not None and len(df_housing) > 0:
            df_h = df_housing[df_housing['project_name'] != 'housing-logo'].copy()
            
            if 'total_properties' not in analytics:
                analytics['total_properties'] = 0
            analytics['total_properties'] += len(df_h)
            
            # Housing specific metrics
            housing_rera = len(df_h[df_h['rera_flag'] == 'Yes'])
            housing_total = len(df_h)
            
            if 'rera_distribution' in analytics:
                analytics['rera_distribution'][0]['count'] += housing_rera
                analytics['rera_distribution'][1]['count'] += (housing_total - housing_rera)
            else:
                analytics['rera_distribution'] = [
                    {"name": "RERA Verified", "count": housing_rera},
                    {"name": "Not Verified", "count": housing_total - housing_rera}
                ]
            
            # Recalculate RERA percentage
            total_rera = analytics['rera_distribution'][0]['count']
            total_props = sum(item['count'] for item in analytics['rera_distribution'])
            analytics['rera_percentage'] = int((total_rera / total_props * 100)) if total_props > 0 else 0
        
        return analytics