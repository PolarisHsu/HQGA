import skimage.io as sio
import numpy as np
import torch
from torchvision import transforms as trn
from torch.autograd import Variable
from skimage.transform import resize
import json
import os
import os.path as osp
import pickle as pkl
import pandas as pd


def set_gpu_devices(n_gpu):
    n_gpu_available = torch.cuda.device_count()
    free_gpus = []
    for i in range(n_gpu_available):
        with torch.cuda.device(i):
            mem_used = torch.cuda.max_memory_allocated()
            if mem_used == 0:
                free_gpus.append(i)
                if len(free_gpus) == n_gpu:
                    break
    if len(free_gpus) < n_gpu:
        print("No enough GPUs, CPU will be used.")
        device = torch.device("cpu")
    else:
        device = torch.device(
            f"cuda:{free_gpus[0]}" if torch.cuda.is_available() else "cpu"
        )
        print("GPU " + ",".join(str(fg) for fg in free_gpus) + " will be used.")
    return device, free_gpus


preprocess = trn.Compose(
    [
        # trn.ToTensor(),
        trn.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]
)


def load_file(filename):
    """
    load obj from filename
    :param filename:
    :return:
    """
    cont = None
    if not osp.exists(filename):
        print("{} not exist".format(filename))
        return cont
    if osp.splitext(filename)[-1] == ".csv":
        # return pd.read_csv(filename, delimiter= '\t', index_col=0)
        return pd.read_csv(filename, delimiter=",")
    with open(filename, "r") as fp:
        if osp.splitext(filename)[1] == ".txt":
            cont = fp.readlines()
            cont = [c.rstrip("\n") for c in cont]
        elif osp.splitext(filename)[1] == ".json":
            cont = json.load(fp)
    return cont


def save_file(obj, filename):
    """
    save obj to filename
    :param obj:
    :param filename:
    :return:
    """
    filepath = osp.dirname(filename)
    if filepath != "" and not osp.exists(filepath):
        os.makedirs(filepath)
    else:
        with open(filename, "w") as fp:
            json.dump(obj, fp, indent=4)


def pkload(file):
    data = None
    if osp.exists(file) and osp.getsize(file) > 0:
        with open(file, "rb") as fp:
            data = pkl.load(fp)
        # print('{} does not exist'.format(file))
    return data


def pkdump(data, file):
    dirname = osp.dirname(file)
    if not osp.exists(dirname):
        os.makedirs(dirname)
    with open(file, "wb") as fp:
        pkl.dump(data, fp)


def to_device(videos, device):
    if isinstance(videos, list):
        return [v.to(device) for v in videos]
    else:
        return videos.to(device)
