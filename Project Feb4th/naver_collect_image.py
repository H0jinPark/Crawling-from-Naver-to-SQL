import os
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm
import time

SAVE_FOLDER = r"/Users/sondaisy/Documents/2024-2/URP/Feb4th Image"

def download_images(url, pbar=None):
    try:
        match = re.search(r"dirId=(\d+)&docId=(\d+)", url)
        if not match:
            if pbar:
                pbar.write(f"Skipping invalid URL: {url}")
            return False

        dirid_docid = f"{match.group(1)}_{match.group(2)}"
        
        # Check if images already exist
        existing_files = [f for f in os.listdir(SAVE_FOLDER) if f.startswith(dirid_docid)]
        if existing_files:
            if pbar:
                pbar.write(f"Already downloaded: {dirid_docid}")
            return True

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            driver.get(url)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            img_tags = soup.find_all("img", class_=lambda c: c and ("rolling_0" in c or "img_rolling_0" in c))
            
            if not img_tags:
                if pbar:
                    pbar.write(f"No images found for: {dirid_docid}")
                return False

            success = False
            for i, img_tag in enumerate(img_tags):
                try:
                    img_url = img_tag.get("src")
                    if img_url:
                        response = requests.get(img_url, 
                                             headers={"User-Agent": "Mozilla/5.0"},
                                             timeout=30)
                        
                        if response.status_code == 200:
                            img_filename = os.path.join(SAVE_FOLDER, f"{dirid_docid}_{i}.jpg")
                            with open(img_filename, "wb") as f:
                                f.write(response.content)
                            success = True
                except Exception as e:
                    if pbar:
                        pbar.write(f"Error downloading image {i} for {dirid_docid}: {str(e)}")
                    continue

            return success

        finally:
            driver.quit()

    except Exception as e:
        if pbar:
            pbar.write(f"Error processing {url}: {str(e)}")
        return False

def process_urls(urls, start_from=None):
    if start_from:
        start_idx = next((i for i, url in enumerate(urls) if start_from in url), 0)
        urls = urls[start_idx:]
        print(f"Starting from index {start_idx} ({len(urls)} URLs remaining)")
    
    with tqdm(total=len(urls), desc="Downloading images") as pbar:
        for url in urls:
            success = download_images(url, pbar)
            pbar.update(1)
            if success:
                pbar.write(f"Successfully processed: {url}")
            time.sleep(1)  # Small delay to prevent overloading

