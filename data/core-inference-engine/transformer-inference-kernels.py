import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from einops import rearrange, repeat
from einops.layers.torch import Rearrange

"""
RD-ViT: Recurrent-Depth Vision Transformer for Semantic Segmentation with Reduced Data Dependence
Paper URL: http://arxiv.org/abs/2605.03999v1

Mathematical Idea:
The Recurrent-Depth Vision Transformer (RD-ViT) addresses the high parameter count of standard Vision Transformers
by employing a recurrent architecture. Instead of stacking 'L' distinct Transformer encoder blocks, RD-ViT
reuses a single (or a small set of) shared Transformer block(s) for 'L' iterations. This significantly
reduces the total number of parameters.

To further enhance efficiency, RD-ViT incorporates an Adaptive Computation Time (ACT) mechanism.
ACT allows the model to dynamically determine the number of recurrent steps required for each input
example. At each recurrent step 't', a 'halting unit' (a small neural network) predicts a raw halting
probability `p_t_raw`. This `p_t_raw` represents the model's confidence that sufficient computation has been
performed for the current input. The model accumulates a weighted sum of the intermediate outputs
from each recurrent step, where the weights are derived from these halting probabilities.
Specifically, for each input in a batch:
1. An initial `remainder` of 1.0 represents the total computation budget for