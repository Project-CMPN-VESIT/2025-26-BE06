import pandas as pd
from pathlib import Path
import json
import re
import os

class CSVAgent:
    def __init__(self, data_dir: str = "data/scraped"):
        self.data_dir = Path(data_dir)
        self.df = None
        self.use_ollama = True
        self._load_housing_data()
        
    def _load_housing_data(self):
        pattern = "housing_processed_*.csv"
        
        search_dirs = [
            self.data_dir,
            Path("data/scraped"),
            Path(__file__).parent / "data" / "scraped",
            Path(__file__).parent.parent / "data" / "scraped",
            Path.cwd() / "data" / "scraped",
        ]
        
        files = []
        for search_dir in search_dirs:
            if search_dir.exists():
                found = list(search_dir.glob(pattern))
                if found:
                    files.extend(found)
                    break
        
        if not files:
            current_dir = Path.cwd()
            for root, dirs, filenames in os.walk(current_dir):
                for filename in filenames:
                    if filename.startswith('housing_processed_') and filename.endswith('.csv'):
                        files.append(Path(root) / filename)
                if files:
                    break
        
        if files:
            latest_file = max(files, key=lambda x: x.stat().st_mtime)
            print(f"Loading CSV from: {latest_file}")
            self.df = pd.read_csv(latest_file)
            self.df = self.df[self.df['project_name'] != 'housing-logo']
            self.df = self.df.dropna(subset=['project_name'])
            print(f"Loaded {len(self.df)} properties")
        else:
            print(f"No housing CSV files found in any search location")
    
    def _parse_price(self, price_str):
        if not price_str or price_str == 'N/A':
            return None
        try:
            price_str = str(price_str).upper().replace('₹', '').replace(',', '').strip()
            if 'C' in price_str or 'CR' in price_str:
                return float(re.findall(r'[\d.]+', price_str)[0]) * 10000000
            elif 'L' in price_str or 'LAC' in price_str:
                return float(re.findall(r'[\d.]+', price_str)[0]) * 100000
            elif 'K' in price_str:
                return float(re.findall(r'[\d.]+', price_str)[0]) * 1000
            else:
                return float(re.findall(r'[\d.]+', price_str)[0])
        except:
            return None
    
    def _get_price_for_bhk(self, row, bhk_type):
        if bhk_type == '1':
            return row.get('2bhk_price', 'N/A')
        elif bhk_type == '2':
            return row.get('2bhk_price', 'N/A')
        elif bhk_type == '3':
            price = row.get('3bhk_price', 'N/A')
            if price == 'N/A':
                price = row.get('3.5bhk_price', 'N/A')
            return price
        elif bhk_type == '4':
            return row.get('3.5bhk_price', 'N/A')
        else:
            return row.get('average_price', 'N/A')
    
    def _extract_filters_with_llm(self, query: str):
        if not self.use_ollama:
            return self._extract_filters_fallback(query)
            
        try:
            import ollama
            
            system_prompt = """Extract search filters from real estate query. Return ONLY valid JSON, no other text.
Format: {"bhk": "2", "locality": "Andheri", "max_price_cr": 2.0, "min_price_cr": null, "rera": true, "ready_to_move": false}
bhk: "1", "2", "3", "4" or null
locality: area name or null
max_price_cr: number in crores or null
min_price_cr: number in crores or null  
rera: true/false/null
ready_to_move: true/false/null"""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Query: {query}"}
            ]
            
            response = ollama.chat(
                model="deepseek-r1:1.5b",
                options={"temperature": 0.0, "num_predict": 200},
                messages=messages
            )
            
            response_text = response["message"]["content"].strip()
            
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].strip()
            
            response_text = response_text.strip()
            if response_text.startswith('{') and response_text.endswith('}'):
                filters = json.loads(response_text)
                print(f"LLM extracted filters: {filters}")
                return filters
            else:
                raise ValueError("Invalid JSON format")
                
        except Exception as e:
            print(f"LLM extraction failed: {e}, using pattern matching")
            self.use_ollama = False
            return self._extract_filters_fallback(query)
    
    def _extract_filters_fallback(self, query: str):
        query_lower = query.lower()
        filters = {}
        
        for bhk in ['1', '2', '3', '4']:
            if f'{bhk} bhk' in query_lower or f'{bhk}bhk' in query_lower:
                filters['bhk'] = bhk
                break
        
        price_patterns = [
            r'under\s+(\d+(?:\.\d+)?)\s*(?:cr|crore)',
            r'below\s+(\d+(?:\.\d+)?)\s*(?:cr|crore)',
            r'less than\s+(\d+(?:\.\d+)?)\s*(?:cr|crore)',
            r'<\s*(\d+(?:\.\d+)?)\s*(?:cr|crore)',
        ]
        
        for pattern in price_patterns:
            price_match = re.search(pattern, query_lower)
            if price_match:
                filters['max_price_cr'] = float(price_match.group(1))
                break
        
        if 'rera' in query_lower or 'approved' in query_lower:
            filters['rera'] = True
        
        if 'ready to move' in query_lower or 'ready-to-move' in query_lower or 'ready' in query_lower:
            filters['ready_to_move'] = True
        
        areas = [
            'andheri west', 'andheri east', 'andheri',
            'powai', 'mulund west', 'mulund east', 'mulund',
            'kandivali west', 'kandivali east', 'kandivali',
            'borivali west', 'borivali east', 'borivali',
            'bandra west', 'bandra east', 'bandra',
            'juhu', 'goregaon west', 'goregaon east', 'goregaon',
            'malad west', 'malad east', 'malad',
            'dahisar', 'mira road', 'virar',
            'thane west', 'thane east', 'thane',
            'ghatkopar', 'vikhroli', 'bhandup',
            'kurla', 'chembur', 'sion'
        ]
        
        for area in areas:
            if area in query_lower:
                filters['locality'] = area.title()
                break
        
        print(f"Fallback extracted filters: {filters}")
        return filters
    
    def query_properties(self, natural_language_query: str, max_results: int = 10):
        if self.df is None or self.df.empty:
            return {
                "success": False,
                "error": "No CSV files found. Please ensure housing_processed_*.csv exists in data/scraped directory."
            }
        
        try:
            filters = self._extract_filters_with_llm(natural_language_query)
            
            filtered_df = self.df.copy()
            
            if filters.get('locality'):
                locality = filters['locality'].lower()
                filtered_df = filtered_df[
                    filtered_df['locality'].str.lower().str.contains(locality, na=False)
                ]
            
            if filters.get('rera') is True:
                filtered_df = filtered_df[filtered_df['rera_flag'] == 'Yes']
            
            if filters.get('ready_to_move') is True:
                filtered_df = filtered_df[filtered_df['ready_to_move'] == 'Yes']
            
            bhk = filters.get('bhk')
            if bhk:
                filtered_df = filtered_df[
                    filtered_df['configuration'].str.contains(bhk, na=False)
                ]
            
            max_price = filters.get('max_price_cr')
            min_price = filters.get('min_price_cr')
            
            if max_price or min_price:
                price_col = f'{bhk}bhk_price' if bhk else 'average_price'
                if price_col not in filtered_df.columns:
                    price_col = 'average_price'
                
                filtered_df['_price_numeric'] = filtered_df[price_col].apply(self._parse_price)
                
                if max_price:
                    max_price_num = max_price * 10000000
                    filtered_df = filtered_df[
                        (filtered_df['_price_numeric'] <= max_price_num) | 
                        (filtered_df['_price_numeric'].isna())
                    ]
                
                if min_price:
                    min_price_num = min_price * 10000000
                    filtered_df = filtered_df[
                        (filtered_df['_price_numeric'] >= min_price_num) |
                        (filtered_df['_price_numeric'].isna())
                    ]
            
            filtered_df = filtered_df.head(max_results)
            
            properties = []
            for _, row in filtered_df.iterrows():
                price = self._get_price_for_bhk(row, bhk) if bhk else row.get('average_price', 'N/A')
                
                properties.append({
                    "project_name": str(row.get('project_name', 'N/A')),
                    "configuration": str(row.get('configuration', 'N/A')),
                    "locality": str(row.get('locality', 'N/A')),
                    "price": str(price),
                    "possession_date": str(row.get('possession_date', 'N/A')),
                    "updated_on": str(row.get('updated_on', 'N/A')),
                    "rera_flag": str(row.get('rera_flag', 'No')),
                    "ready_to_move": str(row.get('ready_to_move', 'No')),
                    "builtup_area": str(row.get('builtup_area', 'N/A'))
                })
            
            interpretation = "Searching for "
            if bhk:
                interpretation += f"{bhk} BHK properties "
            else:
                interpretation += "properties "
            
            if filters.get('locality'):
                interpretation += f"in {filters['locality']} "
            
            if max_price:
                interpretation += f"under ₹{max_price} Cr "
            
            if filters.get('rera'):
                interpretation += "with RERA approval "
            
            if filters.get('ready_to_move'):
                interpretation += "ready to move "
            
            print(f"Found {len(properties)} properties matching: {interpretation}")
            
            return {
                "success": True,
                "query": natural_language_query,
                "interpretation": interpretation.strip(),
                "matches_found": len(properties),
                "properties": properties
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "query": natural_language_query
            }

def query_properties(natural_language_query: str, max_results: int = 10, data_dir: str = "data/scraped"):
    agent = CSVAgent(data_dir=data_dir)
    return agent.query_properties(natural_language_query, max_results)