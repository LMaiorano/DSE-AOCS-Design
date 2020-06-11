#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
title: main
project: DSE-Mars-Reveal
date: 6/10/2020
author: lmaio
"""
from project.subsystems_design.AOCS.vehicle import Orbiter, update_geometry_file
from project.subsystems_design.AOCS.AOCS_design_process import DesignProcess






def orbiter_sizing(file_in, AOCS_des_params):
    update_geometry_file(file_in)

    # Orbiter Vehicle
    O = Orbiter(file_in, AOCS_des_params)
    aerodyn_ignore = []  # ['sa1', 'sa2']#, 'TTC-earth'] # Objects to ignore for aerodynamic cp calculations

    O.vehicle_props(aero_ignore=aerodyn_ignore) # compute vehicle properties

    # ---- Design object -------
    Design = DesignProcess(file_in, AOCS_des_params, O.props)


    ##################################################################
    # Design Process

    # ------ Reaction wheel sizing
    # Max torque by external factors
    max_external_torque, drag, external_torques = Design.worst_torque(O.props)  # [N m] TODO: determine gimbal torques

    # Max angular momemtum capacity to handle cyclic torques (if cyclic torqes add together)
    mom_storage_per_orbit = Design.mom_storage_RW(max_external_torque)  # [N m s]

    # Momentum needed for yaw/roll accuracy (not included in  momentum storage b/c mom to counter this torque is already included)
    mom_for_accuracy = Design.mom_storage_for_accuracy_in_MW(max_external_torque, O.props['pt accuracy'])

    # Torque needed for slew maneuver
    torque_for_slew = Design.slew_torque_RW(Design.mission)

    # Worst case torque needed for moving of solar arrays and HGA
    max_app_T, max_app_h = Design.internal_counter_torque_RW()

    # Calculate worst-case scenario where everything happens at once
    max_possible_T = max_external_torque[1] + max_app_T + torque_for_slew
    max_possible_mom = max_app_h + mom_storage_per_orbit

    if max_possible_mom < mom_for_accuracy:
        raise ValueError('Momentum for accuracy is driving in capacity design')


    # ------ Thruster sizing
    # min thrust to counteract disturbance torqe (likely not a driving factor)
    th_dist_torque = Design.thrust_force_disturbances(max_external_torque)

    # minimum thrust for slew maneuver
    th_slew_maneuver = Design.thrust_force_slewing(Design.mission)

    mom_buildup = Design.secular_momentum(Design.mission)
    th_mom_dump = Design.thrust_force_momentum_dump(mom_buildup, Design.mission['burn_time'])

    life_pulses, pulses = Design.thruster_pulse_life(Design.mission)


    prop_mass = Design.propellent_mass(Design.mission, pulses, th_slew_maneuver, th_mom_dump)

    if prop_mass > Design.params['Prop']['Maintenance fuel mass']:
        raise ValueError(f'Not enough maintenance fuel mass, AOCS needs {prop_mass}')

    # Create hardware requirements
    hw_reqs = {'RW': {'momentum': max_possible_mom,
                      'torque': max_possible_T},
               'IMU':'',
               'star':''}

    hardware_selection = Design.select_hardware(hw_reqs)

    # Size AOCS subsystem
    size = Design.size_AOCS(hardware_selection) # Thrusters and propellant included in propulsion sys








    # --------------- Write to output ---------------------
    # Create separate output dictionary, to prevent accidental mix of in/outputs
    out_params = Design.M.read_excel(file_in, sheet_name='AOCS')


    out_params['O RCS fuel'] = prop_mass
    for key, val in size.items():
        name = 'O '+key
        print(f'{name}: {val}')
        out_params[name] = val

    # Save Values
    Design.M.save_excel(out_params, file_in, 'AOCS')
    # print(prop_mass)

    return hardware_selection

if __name__ == '__main__':
    # Setup -------------------------
    file_in = 'project/subsystems_design/Sub_Output.xlsx'
    AOCS_des_params = 'project/subsystems_design/AOCS/data/desgn_params.xlsx'

    orbiter_sizing(file_in, AOCS_des_params)