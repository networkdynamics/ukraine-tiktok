import json
import os
import random

import dgl
import networkx as nx
from openhgnn.auto import hpo_experiment
from openhgnn.dataset import build_dataset
from openhgnn.experiment import Experiment
from openhgnn.models import build_model
from openhgnn.trainerflow import HeCoTrainer, build_flow, register_flow
from openhgnn.tasks import BaseTask, build_task, register_task
from openhgnn.utils import EarlyStopping, Logger, set_random_seed
from openhgnn.utils.best_config import BEST_CONFIGS
import torch
import transformers

class SocialGraphDataset(dgl.data.DGLDataset):
    """
    Parameters
    ----------
    url : str
        URL to download the raw dataset
    raw_dir : str
        Specifying the directory that will store the
        downloaded data or the directory that
        already stores the input data.
        Default: ~/.dgl/
    save_dir : str
        Directory to save the processed dataset.
        Default: the value of `raw_dir`
    force_reload : bool
        Whether to reload the dataset. Default: False
    verbose : bool
        Whether to print out progress information
    """
    def __init__(self, force_reload=False):

        this_dir_path = os.path.dirname(os.path.abspath(__file__))
        data_dir_path = os.path.join(this_dir_path, '..', '..', 'data')
        raw_dir = os.path.join(data_dir_path, 'raw_graphs')
        save_dir = os.path.join(data_dir_path, 'processed_graphs')

        super().__init__(name='social_graph_dataset',
                         url=None,
                         raw_dir=raw_dir,
                         save_dir=save_dir,
                         force_reload=force_reload,
                         verbose=True)

    def download(self):
        # download raw data to local disk
        pass

    def process(self):
        # process raw data to graphs, labels, splitting masks
        graph_path = os.path.join(self.raw_dir, 'graph_data.json')
        with open(graph_path, 'r') as f:
            graph_data = json.load(f)

        nx_graph = nx.readwrite.node_link_graph(graph_data)

        # REMOVE LATER
        #k = 1000
        #sampled_nodes = random.choices(list(nx_graph.nodes), k=k)
        #nx_graph = nx_graph.subgraph(sampled_nodes)

        user_create_comment = []
        comment_create_user = []
        user_mention_comment = []
        comment_mention_user = []
        user_video = []
        video_user = []
        video_comment = []
        comment_video = []

        node_view = nx_graph.nodes(data=True)
        for u, v, e_data in nx_graph.edges(data=True):

            u_id = int(u)
            v_id = int(v)
            u_data = node_view[u]
            v_data = node_view[v]
            if u_data['type'] == 'user':
                if v_data['type'] == 'comment':
                    if e_data['type'] == 'create':
                        user_create_comment.append(u_id)
                        comment_create_user.append(v_id)

                    elif e_data['type'] == 'mention':
                        user_mention_comment.append(u_id)
                        comment_mention_user.append(v_id)

                elif v_data['type'] == 'video':
                    user_video.append(u_id)
                    video_user.append(v_id)

            elif u_data['type'] == 'video':
                if v_data['type'] == 'user':
                    video_user.append(u_id)
                    user_video.append(v_id)

                elif v_data['type'] == 'comment':
                    video_comment.append(u_id)
                    comment_video.append(v_id)

            elif u_data['type'] == 'comment':
                if v_data['type'] == 'user':
                    if e_data['type'] == 'create':
                        comment_create_user.append(u_id)
                        user_create_comment.append(v_id)

                    elif e_data['type'] == 'mention':
                        comment_mention_user.append(u_id)
                        user_mention_comment.append(v_id)

                elif v_data['type'] == 'video':
                    comment_video.append(u_id)
                    video_comment.append(v_id)

        user_create_comment = torch.tensor(user_create_comment)
        comment_create_user = torch.tensor(comment_create_user)
        user_mention_comment = torch.tensor(user_mention_comment)
        comment_mention_user = torch.tensor(comment_mention_user)
        user_video = torch.tensor(user_video)
        video_user = torch.tensor(video_user)
        video_comment = torch.tensor(video_comment)
        comment_video = torch.tensor(comment_video)

        data_dict = {
            ('user', 'create', 'comment'): (user_create_comment, comment_create_user),
            ('comment', 'create', 'user'): (comment_create_user, user_create_comment),
            ('comment', 'mention', 'user'): (comment_mention_user, user_mention_comment),
            ('user', 'mention', 'comment'): (user_mention_comment, comment_mention_user),
            ('user', 'create', 'video'): (user_video, video_user),
            ('video', 'create', 'user'): (video_user, user_video),
            ('video', 'interaction', 'comment'): (video_comment, comment_video),
            ('comment', 'interaction', 'video'): (comment_video, video_comment)
        }
        self.graph = dgl.heterograph(data_dict)

        # add node attributes

        tokenizer = transformers.RobertaTokenizerFast.from_pretrained('roberta-base')
        language_model = transformers.RobertaModel.from_pretrained('roberta-base')

        video_ids = self.graph.nodes('video')
        user_ids = self.graph.nodes('user')
        comment_ids = self.graph.nodes('comment')
        num_video_nodes = len(video_ids)
        num_video_feats = 784 # size of embedding vector
        video_feats = torch.zeros((num_video_nodes, num_video_feats))
        for video_id in video_ids:
            video_data = node_view[int(video_id)]
            inputs = tokenizer()
            outputs = language_model(inputs)
            embedding = outputs.last_hidden_state[:, 0, :]  # take <s> token (equiv. to [CLS])


    def __getitem__(self, idx):
        # get one example by index
        pass

    def __len__(self):
        # number of data examples
        pass

    def save(self):
        # save processed data to directory `self.save_path`
        file_path = os.path.join(self.save_dir, 'processed_graphs.bin')
        dgl.save_graphs(file_path, [self.graph])

    def load(self):
        # load processed data from directory `self.save_path`
        file_path = os.path.join(self.save_dir, 'processed_graphs.bin')
        graphs, labels = dgl.load_graphs(file_path)
        self.graph = graphs[0]

    def has_cache(self):
        # check whether there are processed data in `self.save_path`
        file_path = os.path.join(self.save_dir, 'processed_graphs.bin')
        return os.path.exists(file_path)


@register_task("embed")
class Embed(BaseTask):
    """Demo task."""
    def __init__(self, args):
        super().__init__()
        self.n_dataset = args.dataset
        self.dataset = build_dataset(args.dataset, 'embed')

    def get_graph(self):
        return self.dataset.g

    def evaluate(self, *args, **kwargs):
        pass

@register_flow("custom_HeCo_trainer")
class CustomHeCoTrainer(HeCoTrainer):

    def __init__(self, args):
        super().__init__(args)

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
        super(CustomHeCoTrainer, self).preprocess()

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
    dataset = SocialGraphDataset()
    task = 'embed'
    gpu = -1
    use_best_config = True
    load_from_pretrained = False
    
    experiment = Experiment(model=model, dataset=dataset, task=task, gpu=gpu,
                            use_best_config=use_best_config, load_from_pretrained=load_from_pretrained)

    configs = BEST_CONFIGS['node_classification']['HeCo']
    for key, value in configs["general"].items():
        experiment.config.__setattr__(key, value)

    for key, value in configs['acm4HeCo'].items():
        experiment.config.__setattr__(key, value)

    experiment.config.logger = Logger(experiment.config)
    set_random_seed(experiment.config.seed)
    trainerflow = 'custom_HeCo_trainer'
    if experiment.config.hpo_search_space is not None:
        # hyper-parameter search
        hpo_experiment(experiment.config, trainerflow)
    else:
        flow = build_flow(experiment.config, trainerflow)
        result = flow.train()
        return result

if __name__ == '__main__':
    main()
