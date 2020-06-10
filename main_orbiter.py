#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
title: main
project: DSE-Mars-Reveal
date: 6/10/2020
author: lmaio
"""
from project.subsystems_design.AOCS.vehicle import Orbiter
from project.subsystems_design.AOCS.AOCS_design_process import DesignProcess



# Setup -------------------------
file_in = 'project/subsystems_design/AOCS/Sub_Output.xlsx'
AOCS_des_params = 'project/subsystems_design/AOCS/data/desgn_params.xlsx'

# Orbiter Vehicle
O = Orbiter(file_in, AOCS_des_params)
aerodyn_ignore = []  # ['sa1', 'sa2']#, 'TTC-earth'] # Objects to ignore for aerodynamic cp calculations

O.vehicle_props(aero_ignore=aerodyn_ignore) # compute vehicle properties

# ---- Design object -------
Design = DesignProcess(file_in, AOCS_des_params, O.props)


##################################################################
# Design Process

# ------ Reaction wheel sizing

orb_max_disturb, drag, _ = Design.worst_torque(O.props)  # [N m] TODO: determine gimbal torques

mom_storage_per_orbit = Design.mom_storage_RW(orb_max_disturb)  # [N m s]

mom_for_accuracy = Design.mom_storage_for_accuracy_in_MW(orb_max_disturb, O.props['pt accuracy'])

torque_for_slew = Design.slew_torque_RW(Design.mission)

# ------ Thruster sizing
# min thrust to counteract disturbance torqe (likely not a driving factor)
th_dist_torque = Design.thrust_force_disturbances(orb_max_disturb)

# minimum thrust for slew maneuver
th_slew_maneuver = Design.thrust_force_slewing(Design.mission)

mom_buildup = Design.secular_momentum(Design.mission)
th_mom_dump = Design.thrust_force_momentum_dump(mom_buildup, Design.mission['burn_time'])

life_pulses, pulses = Design.thruster_pulse_life(Design.mission)

prop_mass = Design.propellent_mass(Design.mission, pulses, th_slew_maneuver, th_mom_dump)


# Create hardware requirements
hw_reqs = {'RW': {'momentum': max(mom_for_accuracy, mom_storage_per_orbit, mom_buildup),
                  'torque': max(torque_for_slew, orb_max_disturb[1])},
           'IMU':'',
           'star':''}

hardware_selection = Design.select_hardware(hw_reqs)

# Size AOCS subsystem
size = Design.size_AOCS(hardware_selection) # needs thrusters and propellant








# --------------- Write to output ---------------------
# Create separate output dictionary, to prevent accidental mix of in/outputs
out_params = Design.M.read_excel(file_in, sheet_name='AOCS')

# Modify values to the new calculated outputs
# out_params['orb_max_disturb_torque'] = list(orb_max_disturb)[1]
# out_params['orb_max_disturb_type'] = list(orb_max_disturb)[0]
# out_params['orb_momentum_storage'] = mom_storage_per_orbit
# out_params['ignored mass bodies'] = aerodyn_ignore
# out_params['aero drag'] = drag
# out_params['thruster pulses'] = life_pulses
# out_params['O min thrust momentum dump'] = th_mom_dump
# out_params['O min thrust slew'] = th_slew_maneuver
out_params['O RCS fuel'] = prop_mass
for key, val in size.items():
    out_params['O '+key] = val

# Save Values
Design.M.save_excel(out_params, file_in, 'AOCS')
# print(prop_mass)