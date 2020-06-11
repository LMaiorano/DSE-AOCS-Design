#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
title: main
project: DSE-Mars-Reveal
date: 6/11/2020
author: lmaio
"""
import warnings
from project.subsystems_design.AOCS.orbiter import orbiter_sizing
from project.subsystems_design.AOCS.probe import probe_sizing

if __name__ == '__main__':
    # Setup -------------------------
    file_in = 'project/subsystems_design/Sub_Output.xlsx'
    AOCS_des_params = 'project/subsystems_design/AOCS/data/desgn_params.xlsx'
    print (' ------------------------------- ')
    print('!!! Update total masses in AOCS/data/desgn_params.xlsx: sheet PRIMARY INPUTS !!!!')
    print(' ------------------------------- ')
    print()

    print('Sizing orbiter ...')
    orbiter_sizing(file_in, AOCS_des_params)

    print('Sizing probe ...')
    probe_sizing(file_in, AOCS_des_params)

    print()
    print(f'Finished. See results in: {file_in}')