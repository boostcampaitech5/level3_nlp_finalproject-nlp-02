import os
import os
import argparse

from pytorch_lightning import Callback
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

def print_trainable_parameters(model):
    """
    Prints the number of trainable parameters in the model.
    """
    trainable_params = 0
    all_param = 0
    for _, param in model.named_parameters():
        all_param += param.numel()
        if param.requires_grad:
            trainable_params += param.numel()
    print(
        f"trainable params: {trainable_params} || all params: {all_param} || trainable%: {100 * trainable_params / all_param}"
    )


class LoRACheckpoint(Callback):
    def __init__(self, monitor, save_top_k, dirpath, mode) :
        super().__init__()
        self.dirpath = dirpath
        self.monitor = monitor
        self.save_top_k = save_top_k
        self.mode = mode
        self.checkpoints = []

    def on_validation_end(self, trainer, pl_module):
        current_value = trainer.callback_metrics.get(self.monitor)
        if current_value is None:
            print(f"Monitored metric {self.monitor} not found.")
            return

        if len(self.checkpoints) < self.save_top_k or self._is_improvement(current_value):
            # Save the model
            filename = self.dirpath + f"/epoch: {trainer.current_epoch} - loss: {current_value:.4f}"
            pl_module.LM.save_pretrained(filename)
            self.checkpoints.append((current_value, filename))

    def _is_improvement(self, current_value):
        worst_value = min(self.checkpoints, key=lambda x: x[0] if self.mode == 'max' else -x[0])[0] if self.checkpoints else None
        return current_value > worst_value if self.mode == 'max' else current_value < worst_value


def save_csv(generated_predict, save_path, folder_name, filename='last'):
    
    generated_predict.to_csv(f'{save_path}/{folder_name}_{filename}_submit.csv', index=False)


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