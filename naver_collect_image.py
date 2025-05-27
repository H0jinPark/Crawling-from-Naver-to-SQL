
# 실행 전에  pip install selenium webdriver-manager beautifulsoup4 requests

import os
import re
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# 이미지 저장 폴더 (로컬 환경 설정)
SAVE_FOLDER = r"C:\Users\user\OneDrive\바탕 화면\urp\naver_image"
os.makedirs(SAVE_FOLDER, exist_ok=True)

def extract_dirid_docid(url):
    """URL에서 dirId와 docId 추출"""
    match = re.search(r"dirId=(\d+)&docId=(\d+)", url)
    if match:
        return f"{match.group(1)}_{match.group(2)}"
    return None

def download_images(url):
    """네이버 지식iN 페이지에서 이미지 다운로드 (로컬 환경)"""
    dirid_docid = extract_dirid_docid(url)
    if not dirid_docid:
        print(" URL에서 dirId 또는 docId를 찾을 수 없습니다.")
        return

    #  Chrome WebDriver 설정
    chrome_options = Options()
    # 필요하면 GUI 모드로 실행 (창을 띄우고 확인 가능)
    # chrome_options.add_argument("--headless")  # GUI 없이 실행할 경우 주석 해제
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    #  ChromeDriver 실행 (자동 설치)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    #  웹 페이지 로드
    driver.get(url)
    time.sleep(3)  # 페이지 로딩 대기 (필요시 증가 가능)

    #  페이지 소스 가져오기
    soup = BeautifulSoup(driver.page_source, "html.parser")

    #  이미지 태그 찾기 (rolling_0 또는 img_rolling_0)
    img_tags = soup.find_all("img", class_=lambda c: c and ("rolling_0" in c or "img_rolling_0" in c))

    if img_tags:
        for i, img_tag in enumerate(img_tags):
            img_url = img_tag.get("src")
            if not img_url:
                continue  # src 속성이 없는 경우 건너뛰기
            
            #  이미지 다운로드
            img_data = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"}).content
            
            #  파일 저장 (파일명: dirId_docId_번호.jpg)
            img_filename = os.path.join(SAVE_FOLDER, f"{dirid_docid}_{i}.jpg")
            with open(img_filename, "wb") as f:
                f.write(img_data)
            
            print(f" 이미지 다운로드 완료: {img_filename}")
    else:
        print(" 이미지를 찾을 수 없습니다.")

    #  WebDriver 종료
    driver.quit()

#  실행 예제 (네이버 지식iN URL 입력)
# url = "https://kin.naver.com/qna/detail.naver?d1id=12&dirId=1205&docId=481218973"  # 원하는 링크로 변경
# download_images(url)
