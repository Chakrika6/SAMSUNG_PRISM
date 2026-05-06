import torch
import torch.nn as nn
import torch.nn.functional as F
import collections.abc
from itertools import repeat

# --- Helper functions and modules (standard Transformer components) ---

def _ntuple(n):
    """Converts input to a tuple of length n. Used for kernel_size, stride, etc."""
    def parse(x):
        if isinstance(x, collections.abc.Iterable):
            return x
        return tuple(repeat(x, n))
    return parse

to_2tuple = _ntuple(2)

def drop_path(x, drop_prob: float = 0., training: bool = False):
    """
    Drop paths (Stochastic Depth) per sample (when applied in main path of residual blocks).
    This is the same as the DropConnect implementation from
    https://github.com/facebookresearch/deepscale/blob/main/deepscale/modules/misc.py
    """
    if drop_prob == 0. or not training:
        return x
    keep_prob = 1 - drop_prob
    # work with diff dim tensors, not just 2D ConvNets
    shape = (x.shape[0],) + (1,) * (x.ndim - 1)
    random_tensor = keep_prob + torch.rand(shape, dtype=x.dtype, device=x.device)
    random_tensor.floor_()  # binarize