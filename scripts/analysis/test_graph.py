import dgl
import torch

g = dgl.graph((torch.tensor([0, 1]), torch.tensor([1, 2])))


hg = dgl.heterograph({
    ('user', 'follows', 'user'): (torch.tensor([0, 1]), torch.tensor([1, 2])),
    ('user', 'plays', 'game'): (torch.tensor([3, 4]), torch.tensor([0, 1]))
})

hg.nodes('user')