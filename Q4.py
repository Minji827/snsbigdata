#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import unquote

def google_search_pdf(keyword, num_results):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.google.com")

    search_box = driver.find_element(By.NAME, "q")
    search_query = f"{keyword} filetype:pdf"
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)

    results = set()
    while len(results) < num_results:
        links = driver.find_elements(By.XPATH, '//a[@href]')
        for link in links:
            href = link.get_attribute('href')
            if href.endswith(".pdf"):
                results.add(href)
        
        if len(results) < num_results:
            try:
                next_button = driver.find_element(By.ID, "pnnext")
                next_button.click()
            except Exception as e:
                print(f"Failed to find more PDFs: {e}")
                break

    driver.quit()
    return list(results)

def download_pdf(url, save_path):
    response = requests.get(url)
    file_name = os.path.join(save_path, unquote(os.path.basename(url)))
    with open(file_name, 'wb') as f:
        f.write(response.content)
    print(f"Downloaded: {file_name}")

def main():
    print("=" * 20)
    print("연습문제 7-4. 구글 사이트에서 pdf 파일을 검색하여 수집하는 크롤러")
    print("=" * 20)
    
    keyword = input("1. 크롤링할 키워드는 무엇입니까?: ")
    num_results = int(input("2. 크롤링 할 건수는 몇건입니까?: "))
    save_path = input("3. 파일이 저장될 경로만 쓰세요 (예: c:\\temp\\): ")
    
    print()
    if not os.path.exists(save_path):
        os.makedirs(save_path)
        print(f"입력하신 경로가 존재하지 않습니다. 경로를 생성하였습니다: {save_path}")
    else:
        print(f"입력하신 경로가 존재하여 {save_path} 폴더에 저장하겠습니다.")
    
    total_downloaded = 0
    pdf_urls = google_search_pdf(keyword, num_results * 2)  # Ensure we get enough URLs
    
    for url in pdf_urls:
        if total_downloaded >= num_results:
            break
        try:
            download_pdf(url, save_path)
            total_downloaded += 1
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            continue
    
    # If not enough PDFs were downloaded, search for more
    while total_downloaded < num_results:
        additional_urls = google_search_pdf(keyword, num_results)
        for url in additional_urls:
            if total_downloaded >= num_results:
                break
            if url not in pdf_urls:  # Avoid downloading the same URLs
                try:
                    download_pdf(url, save_path)
                    total_downloaded += 1
                except Exception as e:
                    print(f"Failed to download {url}: {e}")
                    continue

if __name__ == "__main__":
    main()

