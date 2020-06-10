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
TDS = Design.hardware['MSL Terminal descent']
IMU = Design.hardware['Honeywell MIMU']

# Mass
prop_mass = P.props['probe_mass'] * 0.01666
thruster_sys_mass = prop_mass / 0.8
HW_mass = TDS['mass'] + IMU['mass']*2


# Volume
prop_volume = prop_mass / P.props['cold_gas_rho']
thruster_sys_vol = prop_volume*1.5

IMU_volume = IMU['volume'] *2
TDS_volume = TDS['volume']
HW_volume =  IMU_volume + TDS_volume

# Power
sys_power = IMU['average power']*2 + TDS['average power']



probe_sizing = {'mass w/ HS': round(thruster_sys_mass, 2),
                'volume w/ HS': round(thruster_sys_vol, 4),
                'mass lander': round(HW_mass, 2),
                'volume lander':round(HW_volume, 4),
                'power lander': round(sys_power, 2)}

# Save Data
out_params = Design.M.read_excel(file_in, sheet_name='AOCS')



for key, val in probe_sizing.items():
    out_params['P '+key] = val

# Save Values
Design.M.save_excel(out_params, file_in, 'AOCS')



print(probe_sizing)