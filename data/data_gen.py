import os
import warnings
import openai
import pandas as pd
import time

from tqdm import tqdm

warnings.filterwarnings(action='ignore')

# 설정해 줄 것
# api_key
# csv 경로
# n 설정: 몇 개로 나눠줄 것인가
openai.api_key = ''
n = 2000
df=pd.read_csv('/opt/ml/level3_nlp_finalproject-nlp-02/data/datasets/Velog_summarize.csv',  lineterminator='\n')

def tag(x):
        try:
            text = x[0]
            title = x[1]

            model_name = 'text-davinci-003'

            prompt_user = f'''Instruction: Tell me 5 tags that match the following document. Increase the weight of the Title. Don't be too descriptive. Tags must be noun \n
            Desired format: #English(Korean), #English(Korean), #English(Korean), #English(Korean), #English(Korean) \n
            Title: {title} \n
            Text: {text} \n
            Tags:'''

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
            return response.choices[0].text.strip()
        except Exception as e:
            if "Limit" in str(e):    
                time.sleep(60)
                text = x[0]
                title = x[1]

                model_name = 'text-davinci-003'

                prompt_user = f'''Instruction: Tell me 5 tags that match the following document. Increase the weight of the Title. Don't be too descriptive. Tags must be noun \n
                Desired format: #English(Korean), #English(Korean), #English(Korean), #English(Korean), #English(Korean) \n
                Title: {title} \n
                Text: {text} \n
                Tags:'''

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
