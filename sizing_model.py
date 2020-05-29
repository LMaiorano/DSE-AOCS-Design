#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
title: sizing_model
project: DSE-Mars-Reveal
date: 5/28/2020
author: lmaio
"""


import os
import sys
sys.path.append(os.path.join(os.path.abspath(os.curdir).split('DSE-Mars-Reveal', 1)[0], 'DSE-Mars-Reveal'))


from definitions import MarsReveal
from LuigiPyTools import LatexPandas as LP
import numpy as np
import pandas as pd

M = MarsReveal()


print(f'mu mars: {M.mu_mars}')



