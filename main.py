from Crawling_naver import Crawling_to_CSV
import pandas as pd
# 모듈 형태로 불러온 코드실행(결과적으로 CSV 파일 업데이트)
Crawling_to_CSV()

# 파일 정보 가져오기
questions_new = pd.read_csv("Questions_new.csv")
questions_old = pd.read_csv("Questions_old.csv")
answers_new = pd.read_csv("Answers_new.csv")
answers_old = pd.read_csv("Answers_old.csv")
# 파일 두개 concat하기 (각 데이터들의 고유키 기준 + new로 덮어씌우기)
combined_Q = pd.concat([questions_new, questions_old]).drop_duplicates(subset='문서 번호', keep='first')
combined_A = pd.concat([answers_new, answers_old]).drop_duplicates(subset='답변 ID', keep='first')
#이제 새로운 old파일이 가장 최신 파일이 됨
combined_Q.to_csv('Questions_old.csv', index = False)
combined_A.to_csv('Answers_old.csv', index = False)