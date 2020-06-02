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




# def excel_io_dict(filename, **kwargs):
#     '''Loads parameters from excel file to dictionary
#
#     Args:
#         filename: str
#             Path to Excel file
#         **kwargs: 'sheet_name' or 'columns'
#             To specify specific sheet or columns to load
#             - 'sheet_name'='AOCS' (default)
#             - 'columns' = '['Output name', 'Output Value', 'Units']' (default)
#
#     Returns:
#         Dictionary of parameters
#     '''
#     sheet = kwargs.pop('sheet_name', 'AOCS')
#     cols = kwargs.pop('columns', ['Output name', 'Output Value', 'Units'])
#
#     df = pd.read_excel(filename, sheet_name=sheet, usecols=cols)
#     df.set_index('Output name', inplace=True)
#     df.rename(columns={'Output name': 'name', 'Output Value': 'value', 'Units' : 'units'}, inplace=True)
#     return df.to_dict('index')




if __name__ == '__main__':
    M = MarsReveal()

    file = 'Sub_Output.xlsx'
    params = M.excel_io_dict(file, sheet_name='EPS')
    print(params['test 2']['value'])

