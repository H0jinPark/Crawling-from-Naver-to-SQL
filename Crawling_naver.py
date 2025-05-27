#!/usr/bin/env python
# coding: utf-8

# # 2024-2 URP assignment

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import re
import pandas as pd
from datetime import datetime
from tqdm import tqdm
from naver_collect_image import download_images


# # URL에서 dirID 값을 가져오는 함수

def get_dirid(url):
    match = re.search(r'dirId=(\d+)', url)
    dirid_value = match.group(1)
    if len(dirid_value) >= 6 :
        dirid_value = dirid_value[:6]
    return dirid_value


# # URL에서 docID 값을 가져오는 함수

def get_docid(url):
    match = re.search(r'docId=(\d+)', url)
    docid_value = match.group(1)
    return docid_value


# # 최종적으로 질문과 답변 정보 받아오는 함수

def collect_information(url, Q_df, A_df):
    # 페이지 요청
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)

    # BeautifulSoup으로 페이지 파싱
    soup = BeautifulSoup(response.text, 'html.parser')

    # 질문 제목 추출
    title = soup.find(attrs={'class': 'endTitleSection'}).get_text(strip=True)
    title = title.replace(",","")
    Q_detail= soup.find(attrs={'class': 'questionDetail'}).get_text(strip=True,separator=' ')
    Q_detail = Q_detail.replace(",","")
    Q_info = soup.find_all(class_='infoItem')
    Q_view = Q_info[0].get_text()[3:]
    Q_date = Q_info[1].get_text()[3:]
    if Q_date.endswith(" 전"):
        Q_date = datetime.today().strftime('%Y.%m.%d')
    if Q_date.startswith("작성일"):
        Q_date = Q_date.replace("작성일", "")
    ans = []
    A_dates = []
    user_ids = []
    try:
        answers = soup.find_all(class_='se-main-container')
        ans_date = soup.find_all(class_='answerDate')
        user_id = soup.find_all('strong', class_='name')
        for answer in answers:
            ans.append(answer.get_text(strip=True).replace('\u200b', ''))
        for ans_dates in ans_date:
            A_dates.append(ans_dates.get_text(strip=True))
        for id in user_id:  
            user_ids.append(id.get_text(strip=True))
    except:
        answer_error = "아직 답변이 없습니다"
    ID = get_dirid(url)
    doc_ID = get_docid(url)
    A_inf_list =[]
    n = 1

    for i in range(len(ans)):
        changed = ans[i].replace(","," ")
        if A_dates[i].endswith(" 전"):
            today = datetime.today().strftime('%Y.%m.%d.')
            A_inf_list.append([doc_ID, doc_ID+str(n), user_ids[i], changed[:],today])
        else:
            A_inf_list.append([doc_ID, doc_ID+str(n), user_ids[i], changed[:],A_dates[i]])
        n += 1
    for i in A_inf_list:
        A_df.loc[A_df.shape[0]] = i
    return Q_df, A_df


# # 질문 리스트에서 각 질문의 URL 값 가져오기
# 질문 목록에서 URL만 가져기기

def get_url_from_list(search_url, urls):
    import time
    response = requests.get(search_url) 
    
    soup = BeautifulSoup(response.text, 'html.parser')

    elements = soup.find_all(class_=re.compile(r'^_nclicks:kls_new\.list'))
    
    for element in elements[1:]:
        href = "https://kin.naver.com"+element.get('href')
        urls.append(href)
    time.sleep(1)
    return urls


# ### list 페이지 설정
# ### 삭제 직전인 데이터는 못불러옴 예시로 보여주는 수 밖에 없다. 글로 설명 불가능


def collect_urls(region, Today):
    try:
        urls = []
        for i in range(1,21):
            page = f"https://kin.naver.com/qna/list.naver?dirId={region}&queryTime={Today}%2017%3A33%3A26&page={i}"
            urls= get_url_from_list(page, urls)
    except:
        pass
    print(len(urls))
    return urls

def url_maker(urls):
    import time
    url2 = 'https://kin.naver.com/qna/list.naver?dirId=12'
    headers2 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    current_date = datetime.now()
    Today = current_date.strftime("%Y-%m-%d")

    loc_dict = pd.read_csv("naver_kin_regions_df_l2.csv", index_col = "지역 코드")
    local_lists = loc_dict.index.tolist()

    # # 11월 06일 기준 전체 지역 URL 크롤링(매핑테이블의 index를 사용) -> 현재 지역&플레이스에 나와있는 모든 질문 url을 수집
    for region in tqdm(local_lists, desc="Processing URLs", ncols=100, leave=True):
        region_urls = collect_urls(region, Today)  # 반환값 저장
        time.sleep(1)
        urls.extend(region_urls)  # 반환된 URL을 urls에 추가
    
    print("총 질문 개수:"+str(len(urls)))
    return urls

def Crawling_to_CSV():
    
    # 지역 & 플레이스 기본 정보 문자열 제거를 위한 변수 지정
    url2 = 'https://kin.naver.com/qna/list.naver?dirId=12'
    headers2 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    # 데이터프레임 선언

    Q_df = pd.DataFrame(columns = ['문서 번호', '제목',  '질문',  "위치 고유번호" , '조회수', '질문 날짜'])
    A_df = pd.DataFrame(columns = ['문서 번호', '답변 ID','사용자 ID', '답변', '답변 날짜'])    
    # 오늘 날짜 가져오기
    urls = [] # 혹시 모르니 초기화
    urls = url_maker(urls)

    # # 실제 데이터 불러오기(매핑 테이블 추후 SQL에서 join 예정)
    # ## 45분 정도 소요
    for i in tqdm(range(len(urls)), desc="Processing URLs", ncols=100, leave=True):
        url = urls[i]
        try:
            collect_information(url, Q_df, A_df)
            # # 대찬이형이 만든 이미지 크롤링 코드 추가
            # download_images(url)

        except:
            print(f"질문자가 질문을 삭제했습니다. - {url}")


    Q_df.to_csv('Questions_new.csv', index = False)
    A_df.to_csv('Answers_new.csv', index = False)

# 파일 두개 합치기
'''    
questions_new = pd.read_csv("Questions_new.csv")
questions_old = pd.read_csv("Questions_old.csv")
answers_new = pd.read_csv("Answers_new.csv")
answers_old = pd.read_csv("Answers_old.csv")


combined_Q = pd.concat([questions_new, questions_old]).drop_duplicates(subset='문서 번호', keep='first')
combined_A = pd.concat([answers_new, answers_old]).drop_duplicates(subset='답변 ID', keep='first')
'''

