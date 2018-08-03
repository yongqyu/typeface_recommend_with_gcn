import os
import numpy as np
import scipy.sparse as sp
import torch
from torch.utils import data
from torchvision import transforms
from PIL import Image, ImageOps, ImageFont, ImageDraw


class ImageFolder(data.Dataset):
	"""Load Variaty Chinese Fonts for Iterator."""
	def __init__(self, data_path, image_path, image_size, transform=None):
		"""Initializes image paths and preprocessing module."""
		#self.data_arr = np.load(data_path)
		#shuffle(self.data_arr)

		#self.idx2text = np.load('./data/idx2text.npy')
		#self.idx2typos = np.load('./data/idx2typos.npy')
		#self.typo_list = np.load('./data/typo_list.npy')
		#self.typo_cnt = len(self.typo_list)

		self.image_size = image_size
		self.image_path = image_path
		self.image_paths = list(map(lambda x: os.path.join(image_path, x), os.listdir(image_path)))

		self.transform = transform

	def __getitem__(self, index):
		"""Reads an image from a file and preprocesses it and returns."""
		image = Image.open(self.image_path+str(index)+'.png').convert("L")
		image = image.resize(self.image_size, Image.ANTIALIAS)
		if self.transform is not None:
			image = self.transform(image)

		return index, image

	def __len__(self):
		"""Returns the total number of font files."""
		return len(self.image_paths)

def get_loader(data_path, image_path, image_size, batch_size, num_workers=2):
	"""Builds and returns Dataloader."""

	transform = transforms.Compose([
					transforms.ToTensor(),
					transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

	dataset = ImageFolder(data_path, image_path, image_size, transform)
	data_loader = data.DataLoader(dataset=dataset,
								  batch_size=batch_size,
								  shuffle=False,
								  num_workers=num_workers)
	return data_loader



def normalize(mx):
    """Row-normalize sparse matrix"""
    rowsum = mx.sum(1)
    r_inv = torch.pow(rowsum, -0.5).view(-1)
    #r_inv[torch.isinf(r_inv)] = 0.
    r_mat_inv = torch.diag(r_inv)
    mx = r_mat_inv.mm(mx).t().mm(r_mat_inv)
    return mx


def accuracy(output, labels):
    preds = output.max(1)[1].type_as(labels)
    correct = preds.eq(labels).double()
    correct = correct.sum()
    return correct / len(labels)


import torch
from torch.autograd import Variable

def sort_sequence(data, len_data):

	_, idx_sort = torch.sort(len_data, dim=0, descending=True)
	_, idx_unsort = torch.sort(idx_sort, dim=0)

	sorted_data = data.index_select(0, idx_sort)
	sorted_len = len_data.index_select(0, idx_sort)

	return sorted_data, sorted_len.data.cpu().numpy(), idx_unsort

def unsort_sequence(data, idx_unsort):
	unsorted_data = data.index_select(0, idx_unsort)
	return unsorted_data

def features_to_sequence(features):
	b, c, h, w = features.size()
	features = features.view(b,-1,1,w)

	features = features.permute(0, 3, 1, 2)
	features = features.squeeze(3)
	return features

def accuracy_at_k(pred, label, k=5):
	_, pred  = torch.sort(pred, 1, descending=True)
	batch_size = len(label)
	acc_cnt = sum([l in pred[i,:k] for i, l in enumerate(label)])

	return acc_cnt/batch_size

def baccuracy_at_k(pred, label, k=30):
	label = torch.nonzero(label)
	label_size = label.size(0)
	acc_cnt = sum([j in pred[i,:k] for (i, j) in label])

	return acc_cnt/label_size

def print_network(model, name):
    """Print out the network information."""
    num_params = 0
    for p in model.parameters():
        num_params += p.numel()
    print(model)
    print(name)
    print("The number of parameters: {}".format(num_params))
