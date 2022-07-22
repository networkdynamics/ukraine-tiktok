import argparse
import copy
import dgl
import numpy as np
import torch
import torch.nn as nn
from tqdm import tqdm
import torch.nn.functional as F
from openhgnn.experiment import Experiment
from openhgnn.models import build_model
from openhgnn.models.HeCo import LogReg
from . import BaseFlow, register_flow
from openhgnn.tasks import build_task
from openhgnn.utils import extract_embed, EarlyStopping
from sklearn.metrics import f1_score, roc_auc_score


@register_flow("HeCo_trainer")
class HeCoTrainer(BaseFlow):

    def __init__(self, args):
        super(HeCoTrainer, self).__init__(args)

        self.args = args
        self.model_name = args.model
        self.device = args.device
        self.task = build_task(args)

        self.hg = self.task.get_graph().to(self.device)
        self.num_classes = int(self.task.dataset.num_classes)
        self.args.category = self.task.dataset.category
        
        self.category = self.args.category
        self.pos = self.task.dataset.pos.to(self.device)
        self.model = build_model(self.model).build_model_from_args(self.args, self.hg)
        print("build_model_finish")
        self.model = self.model.to(self.device)

        self.evaluator = self.task.get_evaluator('f1')
        self.optimizer = (
            torch.optim.Adam(self.model.parameters(), lr=args.lr, weight_decay=args.weight_decay))
        self.patience = args.patience
        self.max_epoch = args.max_epoch

        self.train_idx, self.val_idx, self.test_idx = self.task.get_split()
        self.labels = self.task.get_labels().to(self.device)

    def preprocess(self):
        super(HeCoTrainer, self).preprocess()

    def train(self):
        self.preprocess()
        stopper = EarlyStopping(self.args.patience)
        # epoch_iter = tqdm(range(self.max_epoch))
        for epoch in range(self.max_epoch):
            '''use earlyStopping'''
            loss = self._full_train_step()
            early_stop = stopper.loss_step(loss, self.model)
            print((f"Epoch: {epoch:03d}, Loss: {loss:.4f}"))
            
            if early_stop:
                print('Early Stop!\tEpoch:' + str(epoch))
                break
        
        # Evaluation
        model = stopper.load_model(self.model)
        model.eval()
        h_dict = self.model.input_feature()
        embeds = model.get_embeds(self.hg, h_dict=h_dict)

    def _full_train_step(self):
        self.model.train()
        self.optimizer.zero_grad()
        h_dict = self.model.input_feature()
        loss = self.model(self.hg, h_dict, self.pos)
        loss.backward()
        self.optimizer.step()
        loss = loss.cpu()
        loss = loss.detach().numpy()
        return loss

def main():
    model = 'HeCo'
    dataset = 'custom'
    task = 'custom'
    gpu = '1'
    use_best_config = True
    load_from_pretrained = False
    experiment = Experiment(model=model, dataset=dataset, task=task, gpu=gpu,
                            use_best_config=use_best_config, load_from_pretrained=load_from_pretrained)
    experiment.run()
    #trainer = HeCoTrainer()
    #trainer.train()

if __name__ == '__main__':
    main()