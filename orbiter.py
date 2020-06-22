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
import pandas as pd






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
    results = {}

    # ------ Reaction wheel sizing
    # Max torque by external factors
    max_external_torque, external_torques, _ = Design.worst_torque(O.props)  # [N m]
    results.update(external_torques)
    results['Max external torque'] = [max_external_torque[1], 'N m']

    # Max angular momemtum capacity to handle cyclic torques (if cyclic torqes add together)
    mom_storage_per_orbit = Design.mom_storage_RW(max_external_torque)  # [N m s]
    results['Mom storage per orbit'] = [mom_storage_per_orbit, 'N m s']

    # Momentum needed for yaw/roll accuracy (not included in  momentum storage b/c mom to counter this torque is already included)
    mom_for_accuracy = Design.mom_storage_for_accuracy_in_MW(max_external_torque, O.props['pt accuracy'])
    # results['mom min accuracy momentum'] = [mom_for_accuracy, 'N m s']

    # Torque needed for slew maneuver
    torque_for_slew = Design.slew_torque_RW(Design.mission)
    results['RW torque slew'] = [torque_for_slew, 'N m']


    # Worst case torque needed for moving of solar arrays and HGA
    max_app_T, max_app_h = Design.internal_counter_torque_RW()
    results['Max internal dist torque'] = [max_app_T, 'N m']
    results['Max internal dist momentum'] = [max_app_h, 'N m']

    # Calculate worst-case scenario where everything happens at once
    max_possible_T = max_external_torque[1] + max_app_T + torque_for_slew
    max_possible_mom = max_app_h + mom_storage_per_orbit

    if max_possible_mom < mom_for_accuracy:
        # raise ValueError('Momentum for accuracy is driving in capacity design')
        max_possible_mom = mom_for_accuracy

    # ------ Thruster sizing
    # min thrust to counteract disturbance torqe (likely not a driving factor)
    th_dist_torque = Design.thrust_force_disturbances(max_external_torque)

    # minimum thrust for slew maneuver
    th_slew_maneuver = Design.thrust_force_slewing(Design.mission)
    results['Force thrust slew'] = [th_slew_maneuver, 'N']

    mom_buildup = Design.secular_momentum(Design.mission)
    period = 24/Design.mission['mom_dump_freq']
    results[f'Secular momentum buildup per {period}hrs'] = [mom_buildup, 'N m s']

    th_mom_dump = Design.thrust_force_momentum_dump(mom_buildup, Design.mission['burn_time'])
    results['Thrust momentum dump'] = [th_mom_dump, 'N']

    life_pulses, pulses = Design.thruster_pulse_life(Design.mission)
    results['Total thruster pulses'] = [life_pulses, '-']

    prop_mass = Design.propellent_mass(Design.mission, pulses, th_slew_maneuver, th_mom_dump)
    results['Propellant mass'] = [prop_mass, 'kg']

    if prop_mass > Design.params['Prop']['Maintenance fuel mass']:
        raise ValueError(f'Not enough maintenance fuel mass, AOCS needs {prop_mass}')

    # Create hardware requirements
    hw_reqs = {'RW': {'momentum': max_possible_mom,
                      'torque': max_possible_T},
               'IMU':'',
               'star':''}

    hw_sel = Design.select_hardware(hw_reqs)

    # Thrusters and propellant included in propulsion sys
    # Size AOCS subsystem
    size = Design.size_AOCS(hw_sel)

    hw_results = {'Reaction wheels': [hw_sel['RW']['name'], hw_sel['RW']['mass'], hw_sel['RW']['quantity']],
                  'Star sensors': [hw_sel['star']['name'], hw_sel['star']['mass'], hw_sel['star']['quantity']],
                  'Inertial measurement units':[hw_sel['IMU']['name'], hw_sel['IMU']['mass'], hw_sel['IMU']['quantity']]}


    results.update(hw_results)


    tech_results = {'Max external disturbance torque': results['Max external torque'],
                'Max internal disturbance torque': results['Max internal dist torque'],
                'Torque for slew manoeuvre': results['RW torque slew'],
                'Momentum storage for disturbance rejection': results['Mom storage per orbit'],
                f'Secular momentum buildup per {period}hrs': results[f'Secular momentum buildup per {period}hrs'],
                'Thrust force for momentum dump': results['Thrust momentum dump'],
                'Thrust force for slew manoeuvre': results['Force thrust slew'],
                'Total lifetime thruster pulses': results['Total thruster pulses'],
                'Propellant mass':results['Propellant mass']}

    hw_results_df = pd.DataFrame.from_dict(hw_results, orient='index')
    hw_results_df.reset_index(inplace=True)
    hw_results_df = hw_results_df.rename(columns={'index': 'Component',
                                                  0: 'Name',
                                                  1: 'Mass [kg]',
                                                  2: 'Quantity'})

    tech_results_df = pd.DataFrame.from_dict(tech_results, orient='index')
    tech_results_df.reset_index(inplace=True)
    tech_results_df = tech_results_df.rename(columns={'index': 'Parameter',
                                            0: 'Value',
                                            1: 'Units'})



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

    return hw_sel, tech_results_df, hw_results_df


if __name__ == '__main__':
    # Setup -------------------------
    file_in = 'project/subsystems_design/Sub_Output.xlsx'
    AOCS_des_params = 'project/subsystems_design/AOCS/data/desgn_params.xlsx'

    orbiter_sizing(file_in, AOCS_des_params)