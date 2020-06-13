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


import numpy as np

# M = MarsReveal()

class DisturbanceTorques(MarsReveal):
    def __init__(self, file_in):
        super().__init__()
        self.params = self.read_excel(file_in)


    def mag_torque(self, R, M, D):
        '''
        Args:
            R: radius from planet dipole to s/c [km]
            M: magnetic moment of planet    [tesla km^3]
            D: residual dipole of vehicle   [A m^2]

        Returns: magnetic torque on s/c

        '''
        R = R* 10**3
        B = 2 * M / (R**3)
        Tm = D * B
        return Tm, B


    def solar_torque(self, As, Cps, cg, i, q=0.6, **kwargs):
        '''
        Args:
            As: surface area
            Cps: center of solar pressure
            cg: center of gravity
            q: reflectance factor
            i: angle of incidence of the Sun

        Returns: Torque caused by solar radiation pressure

        '''
        if not isinstance(Cps, list) and not isinstance(Cps, tuple):
            Cps = [Cps]
            cg = [cg]
        Fs = kwargs.pop('solar_const', self.solar_irr )
        F = Fs/ self.c * As * (1+q) * np.cos (np.radians(i))
        arm = np.sqrt(sum([(l1 - l2)**2 for (l1, l2) in zip(Cps, cg)]))
        Tsp = F * (arm)
        return Tsp


    def gg_torque(self, R, MOIs, theta_deg, **kwargs):
        '''
        Args:
            R: orbit radius [km]
            Iz: MOI about z [kg m^2]
            Iy: MOI about y [kg m^2]
            theta: max deviation of z-axis from local vertical [rad]
        398600000000000.0
        398600000000000.0
        Returns: Tg, max gravity torque

        '''
        Ix, Iy, Iz = MOIs
        R = R*10**3
        theta = np.radians(theta_deg)
        mu = kwargs.pop('mu', self.mu_mars)
        Tg = 3* mu / (2 * R**3) * abs(Iz - min(Iy, Ix)) * np.sin(2*theta)
        return Tg



    def det_mag_neg(self):
        '''Determine if Magnetic torques can be considered negligible on mars

        Returns: bool, true if mag torque negligible on mars orbit

        '''
        # Earth geostationary magnetic field
        E_r_bound  = 1500 # [km] altitude below which mag field plays significant role
        R_GEO = 6378 + E_r_bound  # [km] radius
        M_earth = 7.96 * 10**15 # [tesla *m^3]

        B_earth = self.mag_torque(R_GEO*10**3, M_earth, 0)[1] * 10**9 # [nT]

        B_mars = 1500 # max magnetic field mars [nT]

        return B_mars < B_earth

    def aero_torque(self, rho, Cd, A, V, Cpa, cg, **kwargs):
        '''Maximum aerodynamic torque

        Args:
            rho: atmospheric density
            Cd: drag coefficient (usually between 2 and 2.5)
            A: Surface area
            V: Spacecraft velocity
            Cpa: Center of aerodynamic pressure
            cg: cenger of gravity

        Returns:
            Maximum torque generated by aerodynamics [N m]
        '''
        D = 0.5 * (rho * Cd * A * V **2)
        if not isinstance(Cpa, list) and not isinstance(Cpa, tuple):
            Cpa = [Cpa]
            cg = [cg]

        arm = np.sqrt(sum([(l1 - l2) ** 2 for (l1, l2) in zip(Cpa, cg)]))
        Ta = D * arm
        return Ta, D












if __name__ == '__main__':
    file_in = 'project/subsystems_design/Sub_Output.xlsx'
    DT = DisturbanceTorques(file_in)

    # # Subsystem Excel filepath, relative to project root.
    # file_in = 'project/subsystems_design/Sub_Output.xlsx'
    #
    # #### Read all inputs ------------
    # in_params = M.read_excel(file_in)
    #
    # #### Access values --------------
    # # params_in['sheetname']['variable name']['column']
    # print(in_params['AOCS']['test 1']['value'])
    #
    #
    #
    #
    # #### Saving output parameters -------------------
    #
    # # Initialize existing sheet, ensures correct dictionary structure
    # out_params = M.read_excel(file_in, sheet_name='AOCS')
    #
    # # Modify values to the new calculated outputs
    # out_params['test 1']['value'] = 'new output 1'



    # # Save Values
    # file_out =  'project/subsystems_design/AOCS/Sub_Output - Copy.xlsx' # Likely same as above
    # M.save_excel(out_params, file_out, 'AOCS')


