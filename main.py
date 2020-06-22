#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
title: main
project: DSE-Mars-Reveal
date: 6/11/2020
author: lmaio
"""
# from
from project.subsystems_design.AOCS.orbiter import orbiter_sizing
from project.subsystems_design.AOCS.probe import probe_sizing

def main():
    # Setup -------------------------
    file_in = 'project/subsystems_design/Sub_Output.xlsx'
    AOCS_des_params = 'project/subsystems_design/AOCS/data/desgn_params.xlsx'
    print(' ------------------------------- ')
    print('!!! Update total masses in AOCS/data/desgn_params.xlsx: sheet PRIMARY INPUTS !!!!')
    print(' ------------------------------- ')
    print()
    # input('< Press enter to confirm masses are up to date>')
    print()

    print('Sizing orbiter ...')
    orb_hw, tech_results, hw_results = orbiter_sizing(file_in, AOCS_des_params)

    save_to_tex(tech_results, 'results/tech_results.tex')
    save_to_tex(hw_results, 'results/hw_results.tex', val_columns=['Mass [kg]', 'Quantity'])

    print()
    print('Sizing probe ...')
    probe_sizing(file_in, AOCS_des_params)

    print()
    print(f'Finished. See results in: {file_in}')


def save_to_tex(design_results, fileout, val_columns=['Value'], sigfigs=3):
    def sci_notation(n):
        if isinstance(n, str):
            return n
        if n == 0:
            s = '0'
        elif n<1e-3:
            s = "%.3e" % (n)
        else:
            s = "%.3f" % (n)
        return s

    design_results[val_columns] = design_results[val_columns].applymap(sci_notation)
    with open(fileout, 'w') as tf:
        tf.write(design_results.to_latex(float_format="%.3E", escape=False, index=False))


if __name__ == '__main__':
    main()
