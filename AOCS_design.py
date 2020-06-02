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
    M = MarsReveal()    # Should be at the top anyways

    # Subsystem Excel filepath, relative to project root.
    file_in = 'project/subsystems_design/AOCS/Sub_Output.xlsx'

    #### Read all inputs ------------
    in_params = M.read_excel(file_in)

    #### Access values --------------
    # params_in['sheetname']['variable name']['column']
    print(in_params['AOCS']['test 1']['value'])




    #### Saving output parameters -------------------

    # Initialize existing sheet, ensures correct dictionary structure
    out_params = M.read_excel(file_in, sheet_name='AOCS')

    # Modify values to the new calculated outputs
    out_params['test 1']['value'] = 'new output 1'



    # Save Values
    file_out =  'project/subsystems_design/AOCS/Sub_Output - Copy.xlsx' # Likely same as above
    M.save_sheet(out_params, file_out, 'AOCS')


