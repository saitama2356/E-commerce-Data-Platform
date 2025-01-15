import requests
import json
import os
import re
import time
from datetime import datetime
import logging
import yaml
from config import TOKEN

# Configure logging
logging.basicConfig(
    filename="scraping_log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Base directory for saving data
BASE_DIR = "D:\\FIA1471\\data"

# Load URLs from YAML file
def read_urls(urls_file):
    with open(urls_file, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config['urls']

# Parse URL to extract item ID, shop ID, and platform
def parse_url(url):
    # Shopee URL pattern
    # if re.match(r'^https://shopee.vn/.*[0-9]+\.[0-9]+$', url):
    #     flag = "shopee"
    #     url_split = url.split('.')
    #     itemid = url_split[-1]
    #     shopid = url_split[-2]

    # Shopee API URL pattern
    if re.match(r'^https://shopee\.vn/api/v4/pdp/hot_sales/get.*item_id=\d+.*shop_id=\d+', url):
        flag = "shopee"
        itemid_match = re.search(r'item_id=(\d+)', url)
        shopid_match = re.search(r'shop_id=(\d+)', url)
        if itemid_match and shopid_match:
            itemid = itemid_match.group(1)
            shopid = shopid_match.group(1)
        else:
            logging.error(f"Invalid Shopee API URL format: {url}")
            return None, None, None


    # Tiki URL pattern
    elif re.match(r'^https:\/\/tiki.vn\/.*\d+.html.*spid=\d+$', url):
        flag = "tiki"
        url_split = re.findall(r"p(\d+).html.*spid=(\d+)", url)
        if url_split:
            itemid, shopid = url_split[0]
        else:
            logging.error(f"Invalid Tiki URL format: {url}")
            return None, None, None
    # Lazada URL pattern
    elif re.match(r'^https:\/\/www\.lazada\.vn\/products\/.*-i\d+-s\d+\.html', url):
        flag = "lazada"
        # Extract itemid and shopid using regex
        match = re.search(r'-i(\d+)-s(\d+)\.html', url)
        if match:
            itemid = match.group(1)  # Extract the number after 'i'
            shopid = match.group(2)  # Extract the number after 's'
        else:
            logging.error(f"Invalid Lazada URL format: {url}")
            return None, None, None
    else:
        logging.error(f"Unsupported URL format: {url}")
        return None, None, None
    
    logging.info(f"Parsed URL: {url} -> itemid: {itemid}, shopid: {shopid}, flag: {flag}")
    return itemid, shopid, flag

# Tiki Scraper with delay between requests
def fetch_tiki(itemid, shopid):
    url = f'https://tiki.vn/api/v2/products/{itemid}?platform=web&spid={shopid}&version=3'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    logging.info(f"Starting Tiki scrape for item_id: {itemid} and shop_id: {shopid} at URL: {url}")
    response = requests.get(url, headers=headers)
    timestamp = datetime.now()

    if response.status_code == 200:
        data = response.json()
        data['scraped_timestamp'] = timestamp.isoformat()
        return data
    else:
        logging.error(f"Failed with status code {response.status_code} and response: {response.text}")
        return None

# Shopee Scraper
def scrape_shopee_product(token, url):
    logging.info(f"Starting Shopee scrape for URL: {url}")
    API_ENDPOINT = "https://continuous-scraper.common.chartedapi.com/scraping-tasks/shopee/run-single"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    payload = {"url": url}
    response = requests.post(API_ENDPOINT, headers=headers, data=json.dumps(payload))
    timestamp = datetime.now()

    if response.status_code == 200:
        result = response.json()
        # Transform result for consistent structure
        result['responseBody'] = json.loads(result['responseBody'])
        result['scraped_timestamp'] = timestamp.isoformat()
        
        # Save result
        item_id = result['responseBody']['data']['item']['item_id']
        save_data(result, "shopee", item_id)
        
        logging.info(f"Successfully scraped Shopee product with item_id {item_id}")
        return result
    else:
        logging.error(f"Shopee scraping failed for URL {url} with status code {response.status_code}")
        return {
            "error": response.status_code,
            "message": response.text,
            "scraped_timestamp": timestamp.isoformat()
        }

# Lazada Scraper with fixes
def scrape_lazada_product(token: str, url: str) -> dict:
    logging.info(f"Starting Lazada scrape for URL: {url}")
    
    API_ENDPOINT = "https://continuous-scraper.common.chartedapi.com/scraping-tasks/lazada/run-single"
    
    headers = {
        "Content-Type": "application/json", 
        "Authorization": f"Bearer {token}"
    }
    
    payload = {
        "url": url,
        "cleanResponseBody": True,  # Get cleaned response format
        "emulateMobileDevice": False  # Use desktop version
    }
    
    response = requests.post(API_ENDPOINT, headers=headers, json=payload)
    timestamp = datetime.now()
    
    if response.status_code == 200:
        try:
            result = response.json()
            
            # Parse the response body if it's a string
            if isinstance(result.get('responseBody'), str):
                result['responseBody'] = json.loads(result['responseBody'])
            
            # Add timestamp
            result['scraped_timestamp'] = timestamp.isoformat()
            
            # Extract item_id
            item_id_match = re.search(r'-i(\d+)-s(\d+)\.html', url)
            if item_id_match:
                item_id = item_id_match.group(1)  # Lazada item ID
                save_data(result, "lazada", item_id)  # Save the data
                logging.info(f"Successfully scraped Lazada product with item_id {item_id}")
            else:
                logging.error(f"Could not extract item_id from URL: {url}")
            
            return result
            
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse Lazada response: {e}")
            return {
                "error": "JSON_PARSE_ERROR",
                "message": str(e),
                "scraped_timestamp": timestamp.isoformat()
            }
    else:
        logging.error(f"Lazada scraping failed for URL {url} with status code {response.status_code}")
        return {
            "error": response.status_code,
            "message": response.text,
            "scraped_timestamp": timestamp.isoformat()
        }

# Save data to JSON file in structured folder
def save_data(data, platform, item_id):
    timestamp = datetime.now()
    date_str = timestamp.date().isoformat()

    # Determine the folder path based on platform
    folder_path = os.path.join(BASE_DIR, platform)
    os.makedirs(folder_path, exist_ok=True)

    # Specify UTF-8 encoding when opening the file
    file_path = os.path.join(folder_path, f"{item_id}_{date_str}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logging.info(f"Data saved to {file_path}")


# Main function to iterate over URLs in YAML file and scrape with delay
def main():
    token = TOKEN
    urls = read_urls("urls.yaml")

    for url in urls:
        itemid, shopid, flag = parse_url(url)
        if flag == "tiki":
            try:
                data = fetch_tiki(itemid, shopid)
                if data:
                    save_data(data, "tiki", itemid)
                else:
                    logging.warning(f"No data returned for Tiki URL: {url}")
            except Exception as e:
                logging.error(f"Failed to scrape Tiki URL {url}: {e}")
                
        # elif flag == "shopee":
        #     # Implement Shopee scraping logic here if required
        #     try:
        #         data = scrape_shopee_product(token, url)
        #         if data:
        #             save_data(data, "shopee", itemid)
        #         else:
        #             logging.warning(f"No data returned for Shopee URL: {url}")

        #     except Exception as e:
        #         logging.error(f"Failed to scrape Shopee URL {url}: {e}")
        
        elif flag == "lazada":
            try:
                data = scrape_lazada_product(token, url)
                    
                if item_id:
                        save_data(data, "lazada", item_id)
                else:
                        logging.warning(f"Failed to determine Lazada item_id for URL: {url}")
            except Exception as e:
                logging.error(f"Failed to scrape Lazada URL {url}: {e}")
            # pass
        # Add delay between requests
        time.sleep(5)

# Run the main function
if __name__ == "__main__":
    logging.info("Starting scraping process")
    main()
    logging.info("Scraping process completed")
