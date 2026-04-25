import asyncio
import random
import pandas as pd
import re
from datetime import datetime
import json
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from pathlib import Path
import uuid

class ScraperService:
    def __init__(self, data_dir="data/scraped"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.data_dir / "scraping_metadata.json"
        self.load_metadata()

    def load_metadata(self):
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {"versions": []}

    def save_metadata(self):
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def create_version_record(self, source, status, records_count=0):
        version_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        version_record = {
            "id": version_id,
            "source": source,
            "timestamp": timestamp,
            "status": status,
            "records_count": records_count,
            "files": []
        }
        
        self.metadata["versions"].append(version_record)
        self.save_metadata()
        return version_record

    async def scrape_99acres(self, pages=5):
        version = self.create_version_record("99acres", "running")
        
        browser_config = BrowserConfig(
            enable_stealth=True, 
            headless=True,
            verbose=False,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            java_script_enabled=True
        )

        crawler_config = CrawlerRunConfig(
            cache_mode="BYPASS",
            check_robots_txt=False, 
            page_timeout=60000      
        )

        base_url = "https://www.99acres.com/search/property/buy/residential-apartments/mumbai?city=12"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_filename = self.data_dir / f"99acres_raw_{timestamp}.txt"
        csv_filename = self.data_dir / f"99acres_processed_{timestamp}.csv"

        try:
            async with AsyncWebCrawler(config=browser_config) as crawler:
                for page_num in range(1, pages + 1):
                    target_url = f"{base_url}?page={page_num}"
                    print(f"Scraping 99acres: Page {page_num}")

                    result = await crawler.arun(
                        url=target_url,
                        config=crawler_config
                    )

                    if result.success:
                        with open(raw_filename, "a", encoding="utf-8") as f:
                            f.write(f"\n\n--- DATA FROM PAGE {page_num} ---\n\n")
                            f.write(result.markdown)
                    else:
                        print(f"Failed to crawl page {page_num}. Error: {result.error_message}")

                    sleep_time = random.uniform(8, 15)
                    await asyncio.sleep(sleep_time)

            # Process the data
            df = self.process_99acres_data(raw_filename)
            df.to_csv(csv_filename, index=False)
            
            version["status"] = "completed"
            version["records_count"] = len(df)
            version["files"] = [str(raw_filename), str(csv_filename)]
            self.save_metadata()
            
            return {"success": True, "version": version, "records": len(df)}
            
        except Exception as e:
            version["status"] = "failed"
            version["error"] = str(e)
            self.save_metadata()
            return {"success": False, "error": str(e)}

    def process_99acres_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()

        pages = re.split(r'--- DATA FROM PAGE \d+ ---', raw_text)
        property_blocks = []
        for page in pages:
            blocks = re.split(r'(?=## \[)', page)
            property_blocks.extend(blocks)

        dataset = []

        for block in property_blocks:
            if len(block.strip()) < 100: continue 

            title_match = re.search(r'## \[\s*(.*?)\s*\]\(', block)
            if not title_match: continue
            full_title = title_match.group(1).strip()
            
            project_match = re.search(r'!\[PROPERTY-IMAGE\].*?\)\s*\n+([^#\n]+)', block)
            if project_match:
                project_name = project_match.group(1).strip()
                project_name = re.sub(r'(RESALE|FEATURED|VERIFIED)', '', project_name, flags=re.I).strip()
            else:
                project_name = "N/A"

            loc_match = re.search(r'in (.*)', full_title)
            locality = loc_match.group(1).strip() if loc_match else "N/A"

            bhk_match = re.search(r'(\d+)\s*BHK', full_title)
            bhk_type = bhk_match.group(0) if bhk_match else "N/A"

            rera_flag = "Yes" if "RERA" in block else "No"
            verified = "Yes" if "GreenVerified" in block else "No"

            price_match = re.search(r'₹[\d,.]+(?:\s*Lac|\s*Cr)?', block)
            price = price_match.group(0) if price_match else "N/A"

            sqft_price_match = re.search(r'₹[\d,.]+\s*/sqft', block)
            sqft_price = sqft_price_match.group(0) if sqft_price_match else "N/A"

            area_match = re.search(r'([\d,]+)\s*sqft', block)
            area = area_match.group(1) if area_match else "N/A"
            
            area_type_match = re.search(r'(Carpet Area|Built-up Area|Super Built-up Area)', block)
            area_type = area_type_match.group(1) if area_type_match else "N/A"

            status_match = re.search(r'(Ready To Move|Under Construction)', block)
            status = status_match.group(1) if status_match else "N/A"

            bath_match = re.search(r'\((\d+)\s*Bath\)', block)
            baths = bath_match.group(1) if bath_match else "N/A"

            furnishing = "N/A"
            if "Unfurnished" in block: furnishing = "Unfurnished"
            elif "Semi-Furnished" in block: furnishing = "Semi-Furnished"
            elif "Furnished" in block: furnishing = "Furnished"

            dealer_match = re.search(r'FEATURED DEALER\n(.*?)\n', block)
            dealer = dealer_match.group(1).strip() if dealer_match else "N/A"
            
            age_match = re.search(r'(\d+[dw]\s*ago|Yesterday|Today)', block)
            updated_on = age_match.group(1) if age_match else "N/A"

            dataset.append({
                "full_title": full_title,
                "locality": locality,
                "bhk": bhk_type,
                "price": price,
                "price_per_sqft": sqft_price,
                "area_sqft": area,
                "area_type": area_type,
                "status": status,
                "rera_flag": rera_flag,
                "bathrooms": baths,
                "furnishing": furnishing,
                "verified": verified,
                "dealer_name": dealer,
                "updated_on": updated_on,
                "project_name": project_name
            })

        return pd.DataFrame(dataset)

    async def scrape_housing(self, pages=5):
        version = self.create_version_record("housing", "running")
        
        browser_config = BrowserConfig(
            enable_stealth=True, 
            headless=True,
            verbose=False,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            java_script_enabled=True
        )

        crawler_config = CrawlerRunConfig(
            cache_mode="BYPASS",
            check_robots_txt=False, 
            page_timeout=60000  
        )

        base_url = "https://housing.com/in/buy/mumbai/property-in-mumbai"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        raw_filename = self.data_dir / f"housing_raw_{timestamp}.txt"
        csv_filename = self.data_dir / f"housing_processed_{timestamp}.csv"

        try:
            async with AsyncWebCrawler(config=browser_config) as crawler:
                for page_num in range(1, pages + 1):
                    target_url = f"{base_url}?page={page_num}"
                    print(f"Scraping Housing: Page {page_num}")

                    result = await crawler.arun(
                        url=target_url,
                        config=crawler_config
                    )

                    if result.success:
                        with open(raw_filename, "a", encoding="utf-8") as f:
                            f.write(f"\n\nDATA FROM PAGE {page_num}\n\n")
                            f.write(result.markdown)
                    else:
                        print(f"Failed to crawl page {page_num}. Error: {result.error_message}")

                    sleep_time = random.uniform(8, 15)
                    await asyncio.sleep(sleep_time)

            # Process the data
            df = self.process_housing_data(raw_filename)
            df.to_csv(csv_filename, index=False)
            
            version["status"] = "completed"
            version["records_count"] = len(df)
            version["files"] = [str(raw_filename), str(csv_filename)]
            self.save_metadata()
            
            return {"success": True, "version": version, "records": len(df)}
            
        except Exception as e:
            version["status"] = "failed"
            version["error"] = str(e)
            self.save_metadata()
            return {"success": False, "error": str(e)}

    def process_housing_data(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_text = f.read()

        project_blocks = re.split(r'Zero Brokerage|Verified', raw_text)

        dataset = []

        for block in project_blocks:
            if not block.strip(): continue

            name_match = re.search(r'\[(.*?)\]', block)
            if not name_match: continue
            
            config_loc_match = re.search(r'## (.*?) in (.*?), (?:Mumbai|Vasai|Nala Sopara|Thane)', block)
            
            pos_match = re.search(r'Possession: (.*?)(?:\n|$)', block)
            avg_price_match = re.search(r'Avg. Price: (.*?)(?:Possession|Updated|$)', block)
            
            updated_match = re.search(r'Updated\s+\n(.*?)\n', block)
            
            rera_flag = "Yes" if "RERA" in block else "No"
            
            ready_to_move = "Yes" if "Ready to move" in block else "No"
            builtup_match = re.search(r'(\d+ sq.ft)\nBuiltup area', block)
            
            def get_bhk_price(bhk_type):
                match = re.search(rf'{bhk_type} Flat\n(₹[\d\.]+ [CL](?: - [\d\.]+ [CL])?)', block)
                return match.group(1) if match else "N/A"

            if name_match:
                entry = {
                    "project_name": name_match.group(1).strip(),
                    "configuration": config_loc_match.group(1) if config_loc_match else "N/A",
                    "locality": config_loc_match.group(2) if config_loc_match else "N/A",
                    "2bhk_price": get_bhk_price("2 BHK"),
                    "3bhk_price": get_bhk_price("3 BHK"),
                    "3.5bhk_price": get_bhk_price("3.5 BHK"),
                    "average_price": avg_price_match.group(1).strip() if avg_price_match else "N/A",
                    "possession_date": pos_match.group(1).strip() if pos_match else "N/A",
                    "updated_on": updated_match.group(1).strip() if updated_match else "N/A",
                    "rera_flag": rera_flag,
                    "ready_to_move": ready_to_move,
                    "builtup_area": builtup_match.group(1) if builtup_match else "N/A"
                }
                dataset.append(entry)

        return pd.DataFrame(dataset)

    def get_versions(self, limit=10):
        versions = self.metadata.get("versions", [])
        versions.sort(key=lambda x: x["timestamp"], reverse=True)
        return versions[:limit]

    def get_version_details(self, version_id):
        for version in self.metadata.get("versions", []):
            if version["id"] == version_id:
                return version
        return None