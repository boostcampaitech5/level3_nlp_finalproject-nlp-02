import torch

class WarmupConstantLR(torch.optim.lr_scheduler.LambdaLR):
    """ Linear warmup and then constant.
        Linearly increases learning rate schedule from 0 to 1 over `warmup_steps` training steps.
        Keeps learning rate schedule equal to 1. after warmup_steps.
    """
    def __init__(self, optimizer, warmup_steps, last_epoch=-1):
        

        def lr_lambda(step):
            step+=1

            if step < warmup_steps+1:
                return float(step) / float(max(1.0, warmup_steps+1))
            return 1.

        super(WarmupConstantLR, self).__init__(optimizer, lr_lambda, last_epoch=last_epoch)
        
        
class WarmupDecayLR(torch.optim.lr_scheduler._LRScheduler):
    def __init__(self, optimizer, warmup_steps, total_steps, last_epoch=-1):
        self.warmup_steps = warmup_steps
        self.total_steps = total_steps
        super(WarmupDecayLR, self).__init__(optimizer, last_epoch)

    def get_lr(self):
        step = self.last_epoch
        if step < self.warmup_steps:
            return [base_lr * (0.1 + 0.9 * step / self.warmup_steps) for base_lr in self.base_lrs]
        else:
            return [base_lr * (self.total_steps - step) / (self.total_steps - self.warmup_steps) for base_lr in self.base_lrs]