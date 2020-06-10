#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
title: main_probe
project: DSE-Mars-Reveal
date: 6/10/2020
author: lmaio
"""



from project.subsystems_design.AOCS.vehicle import Probe
from project.subsystems_design.AOCS.AOCS_design_process import DesignProcess

file_in = 'project/subsystems_design/AOCS/Sub_Output.xlsx'
AOCS_des_params = 'project/subsystems_design/AOCS/data/desgn_params.xlsx'

P = Probe(file_in, AOCS_des_params)

Design = DesignProcess(file_in, AOCS_des_params, P.props, vehicle='probe')



# rough sizing
prop_mass = P.props['probe_mass'] * 0.01666
IMU_mass = 1.5 * 2
sys_mass = prop_mass/ 0.8

prop_volume = prop_mass / P.props['cold_gas_rho']
IMU_volume = 0.015877*2
TDS_volume = 0
sys_volume = prop_volume + IMU_volume + TDS_volume


probe_sizing = {'mass': sys_mass,
                'volume': sys_volume}

# Save Data
out_params = Design.M.read_excel(file_in, sheet_name='AOCS')



for key, val in probe_sizing.items():
    out_params['P '+key] = val

# Save Values
Design.M.save_excel(out_params, file_in, 'AOCS')



print(P.props)