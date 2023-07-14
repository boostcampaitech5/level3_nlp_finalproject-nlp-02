import os
import argparse

from datetime import datetime, timezone, timedelta
from glob import glob


def get_folder_name(CFG, args):
    """
    실험 결과를 기록하기 위해 초 단위 날짜 정보를 고유 키로 선정
    """
    now = datetime.now(tz=timezone(timedelta(hours=9)))
    folder_name = f"{now.strftime('%m-%d_%H:%M:%S')}_{CFG['name']}_{args.exp_name}"
    save_path = f"./results/{folder_name}"
    CFG['save_path'] = save_path
    os.makedirs(save_path)

    return folder_name, save_path


def get_best_check_point(save_path):
    """
    가장 최근 체크포인트로 학습된 모델을 가져오는 메소드
    """
    check_point_list = glob(f'{save_path}/*/*/*/epoch*')
    check_point_list.sort(reverse=True)

    last_check_point = check_point_list[0]

    return last_check_point

# 아직 미사용
def get_add_special_tokens():
    arr = ['[OTH]', '[ENT]', '[/ENT]', '[SUB]', '[OBJ]', '[PER]', '[LOC]', '[POH]', '[DAT]', '[NOH]', '[ORG]']

    # entity detail
    for category in ['S', 'O']:
        for type in ['PER', 'NOH', 'ORG', 'LOC', 'POH', 'DUR', 'PNT', 'TIM', 'MNY', 'DAT']:
            arr.append(f"[{category}:{type}]")
            arr.append(f"[/{category}:{type}]")
    
    return arr


def save_csv(submit, pred_label, probs, save_path, folder_name, filename='last'):
    submit['pred_label'] = pred_label
    submit['probs'] = probs
    submit.to_csv(f'{save_path}/{folder_name}_{filename}_submit.csv', index=False)


if __name__ == "__main__":
    # args로 실험명 지정 받기
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--exp_name', type=str)
    args = parser.parse_args()

    if args.exp_name is None:
        print("실험명을 입력해주세요")
        exit()

    now = datetime.now(tz=timezone(timedelta(hours=9)))
    folder_name = now.strftime('%m-%d-%H:%M:%S') + f"_{'테스트'}" + f"_{args.exp_name}"
    
    print(folder_name)