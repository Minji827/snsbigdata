#!/usr/bin/env python
# coding: utf-8

# In[4]:


import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def search_videos(driver, keyword, max_results):
    search_url = "https://www.youtube.com/results?search_query=" + keyword
    driver.get(search_url)
    time.sleep(2)

    video_links = []
    while len(video_links) < max_results:
        videos = driver.find_elements(By.XPATH, '//*[@id="video-title"]')
        for video in videos:
            if len(video_links) >= max_results:
                break
            link = video.get_attribute('href')
            if link and link not in video_links:
                video_links.append(link)
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(2)

    return video_links[:max_results]

def get_comments(driver, video_url, max_comments):
    driver.get(video_url)
    time.sleep(2)

    comments = []
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
    time.sleep(2)

    while len(comments) < max_comments:
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        time.sleep(2)
        comment_elements = driver.find_elements(By.XPATH, '//*[@id="content-text"]')
        author_elements = driver.find_elements(By.XPATH, '//*[@id="author-text"]')
        date_elements = driver.find_elements(By.XPATH, '//*[@id="published-time-text"]')

        for i in range(len(comment_elements)):
            if len(comments) >= max_comments:
                break
            author = author_elements[i].text if i < len(author_elements) else "Unknown"
            date = date_elements[i].text if i < len(date_elements) else "Unknown"
            comments.append({
                'URL주소': video_url,
                '댓글작성자명': author,
                '댓글작성일자': date,
                '댓글내용': comment_elements[i].text
            })

    return comments[:max_comments]

def save_to_txt(comments, folder_name):
    with open(os.path.join(folder_name, 'comments.txt'), 'w', encoding='utf-8') as f:
        for i, comment in enumerate(comments, start=1):
            f.write(f"1. URL 주소: {comment['URL주소']}\n")
            f.write(f"2. 댓글 작성자명: {comment['댓글작성자명']}\n")
            f.write(f"3. 댓글 작성일자: {comment['댓글작성일자']}\n")
            f.write(f"4. 댓글 내용: {comment['댓글내용']}\n")
            f.write("-" * 20 + "\n")

def save_to_csv(comments, folder_name):
    df = pd.DataFrame(comments)
    df.index += 1
    df.index.name = '순번'
    df.to_csv(os.path.join(folder_name, 'comments.csv'), index=True, encoding='utf-8-sig')

def save_to_xls(comments, folder_name):
    df = pd.DataFrame(comments)
    df.index += 1
    df.index.name = '순번'
    df.to_excel(os.path.join(folder_name, 'comments.xlsx'), index=True, encoding='utf-8-sig')

def main():
    print("= " * 20)
    print("연습문제 8-3 유튜브 영상의 댓글 수집학")
    print("= " * 20)
    
    keyword = input("1. 유튜브에서 검색할 주제 키워드를 입력하세요(예: 롯데마트): ")
    num_videos = int(input("2. 위 주제로 댓글을 크롤링할 유튜브 영상은 몇건입니까?: "))
    num_comments = int(input("3. 각 동영상에서 추출할 댓글은 몇건입니까?: "))
    folder_name = input("4. 크롤링 결과를 저장할 폴더명만 쓰세요(예: c:\\temp\\): ")
    
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    driver = init_driver()

    videos = search_videos(driver, keyword, num_videos)
    all_comments = []

    for i, video_url in enumerate(videos):
        print(f"{i+1}번째 영상의 댓글을 수집 중입니다...")
        comments = get_comments(driver, video_url, num_comments)
        for j, comment in enumerate(comments):
            print(f"{i+1}번째 영상의 {j+1}번째 댓글")
            print("-" * 20)
            print(f"1. URL 주소: {comment['URL주소']}")
            print(f"2. 댓글 작성자명: {comment['댓글작성자명']}")
            print(f"3. 댓글 작성일자: {comment['댓글작성일자']}")
            print(f"4. 댓글 내용: {comment['댓글내용']}")
            all_comments.append(comment)
            print("\n")
    
    save_to_txt(all_comments, folder_name)
    save_to_csv(all_comments, folder_name)
    save_to_xls(all_comments, folder_name)
    print("크롤링이 완료되었습니다. 결과가 저장되었습니다.")
    
    driver.quit()

if __name__ == "__main__":
    main()


# In[ ]:




