# -*- coding: utf-8 -*-
"""
Created on Fri May  6 18:04:40 2022

@author: ThinkPad
"""
import torch.nn.functional as F
import time
import torch
import torch.nn as nn
import numpy as np
from torch.autograd import Variable


import conv_modules
import custom_layers
import geometry
import hyperlayers
import model
from torchmeta.modules import (MetaModule, MetaSequential)
from collections import OrderedDict



class PointNetCls(nn.Module):
    def __init__(self, k=2, feature_transform=False):
        super(PointNetCls, self).__init__()
        self.latent_dim = 256
        self.feature_transform = feature_transform
        self.feat = model.PointNetfeat(global_feat=True, feature_transform=feature_transform)
        self.phi = custom_layers.FCBlock(outputDim = k)
       
        self.hyper_phi = hyperlayers.HyperNetwork(hyper_in_features=self.latent_dim,
                                                          hyper_hidden_layers=1,
                                                          hyper_hidden_features=self.latent_dim,
                                                          hypo_module=self.phi)
        def forward(self, x, z):
            x, trans, trans_feat = self.feat(x)
            phi_weights = self.hyper_phi(z)
            phi = lambda i: self.phi(i, params=phi_weights)
            x = phi(x)
            
            return F.log_softmax(x, dim=1), trans, trans_feat
        
class PointnetHyper(MetaModule):
    def __init__(self,
                 outputDim = 1,
                 activation='relu',
                 nonlinearity='relu'):
        super().__init__()

        self.net = []
        self.net.append(custom_layers.FCLayer(in_features=1024, out_features=512, nonlinearity='relu', norm='layernorm'))
        self.net.append(custom_layers.FCLayer(in_features=512, out_features=256, nonlinearity='relu', norm='layernorm'))
        self.net.append(custom_layers.FCLayer(in_features=256, out_features=outputDim, nonlinearity=None, norm=None))

        self.net = MetaSequential(*self.net)
        self.net.apply(custom_layers.init_weights_normal)

    def forward(self, input, params=None):
        return self.net(input, params=self.get_subdict(params, 'net'))
    
    
    
if __name__ == '__main__':
    sim_data = Variable(torch.rand(32,3,2500))

    cls = PointNetCls(k = 5)
    out, _, _ = cls(sim_data)
    print('class', out.size())
