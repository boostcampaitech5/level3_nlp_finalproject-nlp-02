import os
import warnings
import openai
import pandas as pd

from tqdm import tqdm

warnings.filterwarnings(action='ignore')

# 설정해 줄 것
# api_key
# csv 경로
# n 설정: 몇 개로 나눠줄 것인가
openai.api_key = ''
n = 2000
# df=pd.read_csv('/opt/ml/level3_nlp_finalproject-nlp-02/data/datasets/Velog_summarize.csv',  lineterminator='\n')
df=pd.read_csv('/opt/ml/level3_nlp_finalproject-nlp-02/data/datasets/dataset/Velog/Velog_summarize_00000.csv',  lineterminator='\n')
# df = df.head(18).copy()

def tag(x):
        try:
            text = x[0]
            title = '\n≈'+x[1]+'≈\n'

            model_name = 'text-davinci-003'

            prompt_user = '''Q: ᴥ{}ᴥ 사이에 들어갈 문서에 어울리는 5개의 태그를 작성해 줘.\n 
            추가정보1: 형식은 #한글태그(english)\n
            추가정보2: 한글로만 이루어진 문서라도 #한글(english) 형식 지켜서 작성해 줘.\n 
            추가정보3: ≈{}≈사이에 들어가는건 문서의 제목이니 가중치를 높여 줘.\n
            ᴥ''' + title+ text + "\nᴥ \nA:"

            response = openai.Completion.create(
            model = model_name,
            prompt = prompt_user,
            temperature = 0,
            max_tokens = 140,
            top_p = 1,
            frequency_penalty = 0.0,
            presence_penalty = 0.0,
            stop =["\n"]
            )
            return response.choices[0].text.strip()
        except Exception as e:
            if "Limit" in str(e):    
                time.sleep(60)
                text = x[0]
                title = '\n≈'+x[1]+'≈\n'

                model_name = 'text-davinci-003'

                prompt_user = '''Q: ᴥ{}ᴥ 사이에 들어갈 문서에 어울리는 5개의 태그를 작성해 줘.\n 
                추가정보1: 형식은 #한글태그(english)\n
                추가정보2: 한글로만 이루어진 문서라도 #한글(english) 형식 지켜서 작성해 줘.\n 
                추가정보3: ≈{}≈사이에 들어가는건 문서의 제목이니 가중치를 높여 줘.\n
                ᴥ''' + title+ text + "\nᴥ \nA:"

                response = openai.Completion.create(
                model = model_name,
                prompt = prompt_user,
                temperature = 0,
                max_tokens = 140,
                top_p = 1,
                frequency_penalty = 0.0,
                presence_penalty = 0.0,
                stop =["\n"]
                )
                
                return response.choices[0].text.strip()

for i in range(len(df)//n):
  print('---------------------'+str(i*n).zfill(5),str((i+1)*n).zfill(5)+'---------------------')
  df_tmp = df.iloc[i*n:(i+1)*n].copy()
  tqdm.pandas()
  print(len(df_tmp))
  df_tmp['tag'] = df_tmp[['summarize','title']].progress_apply(lambda x: tag(x), axis=1)
  print('making csv...')
  df_tmp.to_csv('/opt/ml/level3_nlp_finalproject-nlp-02/data/datasets/dataset/Velog/Velog_tag_'+str(i*n).zfill(5)+'.csv', sep=',', na_rep='NaN',index=False) # do not write index
  print('DONE!')

print('---------------------'+str((i+1)*n).zfill(5),str((i+1)*n+(len(df)%n)).zfill(5)+'---------------------')
df_tmp = df.iloc[(i+1)*n:(i+1)*n+(len(df)%n)].copy()
tqdm.pandas()
print(len(df_tmp))
df_tmp['tag'] = df_tmp[['summarize','title']].progress_apply(lambda x: tag(x), axis=1)
print('making csv...')
df_tmp.to_csv('/opt/ml/level3_nlp_finalproject-nlp-02/data/datasets/dataset/Velog/Velog_tag_'+str((i+1)*n).zfill(5)+'.csv', sep=',', na_rep='NaN',index=False) # do not write index
print('DONE!')
