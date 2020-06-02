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


from definitions import MarsReveal, ROOT_DIR
from LuigiPyTools import LatexPandas as LP
import numpy as np
import pandas as pd
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import openpyxl.utils.dataframe as pxl




if __name__ == '__main__':
    M = MarsReveal()

    file = 'project/subsystems_design/AOCS/Sub_Output.xlsx'
    EPS_params = M.read_excel(file, sheet_name='EPS')


    out_params = M.read_excel(file, sheet_name='AOCS')

    out_params['test 1']['value'] = 'lol'

    M.save_excel(out_params, 'project/subsystems_design/AOCS/Sub_Output - Copy.xlsx', 'AOCS')


