#   Copyright (c) 2020 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Tensor utility."""

from itertools import chain

import numpy as np
import paddle
import paddle.fluid as fluid
import paddle.fluid.core as core
from paddle.nn.layer.transformer import MultiHeadAttention


def get_tensor(tensor_name):
    tensor = fluid.global_scope().find_var(tensor_name).get_tensor()
    if tensor is None:
        return None
    return np.array(tensor)


def pad_batch_data(insts, pad_id=0):
    """Pad the instances to the max sequence length in batch. """
    max_len = max(map(len, insts))
    inst_data = np.array([list(inst) + [pad_id] * (max_len - len(inst)) for inst in insts])
    return inst_data.astype("int64").reshape([-1, max_len])


def repeat(x, times):
    """Repeate tensor."""
    if isinstance(x, dict):
        return {k: repeat(v, times) for k, v in x.items()}
    elif isinstance(x, list):
        return [repeate(v, times) for v in x]
    elif isinstance(x, paddle.Tensor):
        return paddle.tile(x, [times] + [1] * (len(x.shape) - 1))
    else:
        return x


def gather(x, index):
    """Gather data by 1D index."""
    if isinstance(x, MultiHeadAttention.Cache):
        return MultiHeadAttention.Cache(gather(x.k, index), gather(x.v, index))
    elif isinstance(x, dict):
        return {k: gather(v, index) for k, v in x.items()}
    elif isinstance(x, list):
        return [gather(v, index) for v in x]
    elif isinstance(x, paddle.Tensor):
        return paddle.gather(x, index)
    else:
        return x