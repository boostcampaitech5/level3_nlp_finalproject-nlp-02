import os
import warnings
import openai
import pandas as pd

from tqdm import tqdm

warnings.filterwarnings(action='ignore')

# 설정해 줄 것
# api_key
# csv 경로
# index
openai.api_key = ''
df=pd.read_csv('/opt/ml/level3_nlp_finalproject-nlp-02/data/datasets/Tistory_summarize.csv')
index = 10
text = df.iloc[index]['summarize']
title = '\n≈'+df.iloc[index]['title']+'≈\n'

model_name = 'text-davinci-003'

prompt_user = '''Q: ᴥ{}ᴥ 사이에 들어갈 문서에 어울리는 5개의 태그를 알려줘. 
추가 정보1: 태그 형식은 #영어(한글). \n 
추가 정보2: 한글로만 이루어진 문서라도 #english(한글)이렇게 작성해 줘.\n 
추가 정보3: ≈{}≈사이에 들어가는건 문서의 제목이니 가중치를 높여 줘. \n
ᴥ''' + title+ text + " ᴥ \n A: "

response = openai.Completion.create(
    model = model_name,
    prompt = prompt_user,
    temperature = 0,
    max_tokens = 100,
    top_p = 1,
    frequency_penalty = 0.0,
    presence_penalty = 0.0,
    stop =["\n"]
)
print(prompt_user)
print(response.choices[0].text.strip())