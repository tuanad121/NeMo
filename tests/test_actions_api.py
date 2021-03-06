# ! /usr/bin/python
# -*- coding: utf-8 -*-

# Copyright 2019 NVIDIA. All Rights Reserved.
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
# =============================================================================

import os

import nemo
from tests.common_setup import NeMoUnitTest


class TestTrainers(NeMoUnitTest):
    def test_checkpointing(self):
        path = 'optimizer.pt'
        optimizer = nemo.backends.pytorch.actions.PtActions()
        optimizer.save_state_to(path)
        optimizer.step = 123
        optimizer.epoch_num = 324
        optimizer.restore_state_from(path)
        self.assertEqual(optimizer.step, 0)
        self.assertEqual(optimizer.epoch_num, 0)
        self.assertEqual(len(optimizer.optimizers), 0)
        os.remove(path)

    def test_multi_optimizer(self):
        path = 'optimizer.pt'
        module = nemo.backends.pytorch.common.SequenceEmbedding(voc_size=8, hidden_size=16)
        optimizer = nemo.backends.pytorch.actions.PtActions()
        optimizer.create_optimizer("sgd", module, optimizer_params={"lr": 1.0})
        optimizer.create_optimizer("sgd", [module], optimizer_params={"lr": 2.0})
        optimizer.create_optimizer("novograd", [module], optimizer_params={"lr": 3.0})
        optimizer.create_optimizer("adam", [module], optimizer_params={"lr": 4.0})
        optimizer.create_optimizer("adam_w", [module], optimizer_params={"lr": 5.0})
        self.assertEqual(len(optimizer.optimizers), 5)
        optimizer.save_state_to(path)
        optimizer.step = 123
        optimizer.epoch_num = 324
        for i, opt in enumerate(optimizer.optimizers):
            for param_group in opt.param_groups:
                self.assertEqual(param_group['lr'], float(i + 1))
                param_group['lr'] = i
        optimizer.restore_state_from(path)
        for i, opt in enumerate(optimizer.optimizers):
            for param_group in opt.param_groups:
                self.assertEqual(param_group['lr'], float(i + 1))
        self.assertEqual(optimizer.step, 0)
        self.assertEqual(optimizer.epoch_num, 0)
        self.assertEqual(len(optimizer.optimizers), 5)
        os.remove(path)
