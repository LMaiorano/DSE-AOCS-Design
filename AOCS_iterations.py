#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
title: AOCS_iterations
project: DSE-Mars-Reveal
date: 6/8/2020
author: lmaio
"""
import numpy as np
from project.subsystems_design.AOCS.AOCS_sizing_models import HardwareSizing, DisturbanceTorques
from definitions import MarsReveal

class DesignProcess(MarsReveal):
    def __init__(self, params_file):
        super().__init__()
        self.params_file = params_file
        self.params = self.read_excel(self.params_file)


    def id_max_torque(self, veh_props):
        DT = DisturbanceTorques(self.params_file)

        h_orbit = self.params['Astro']['h']
        orb_radius = self.R_mars + h_orbit



        # ------- Inputs -------
        # Magnetic
        orbiter_dipole = veh_props['dipole']  # [A m^2] residual dipole TODO: value unkown
        # Solar Radiation
        Cps = veh_props['c_pres solar']  # TODO: value unknown
        Cg = veh_props['cg']
        i = veh_props['solar incidence']

        # Gravity gradient
        theta = veh_props['pt excursion']  # Max excursion from nadir SC pointing

        # Aerodynamics
        Cpa = veh_props['c_pres aero']
        Cd = veh_props['Cd']


        # ------------- Calculations -------------
        moi = self.sc_moment_of_inertia(veh_props['mass'], veh_props['dims'], shape=veh_props['shape'])
        # Magnetic torque
        Mag_mars = (5 * 10 ** -8) * (3397 ** 3) / 2  # [T km^3] from Elements of S/c Engineering, Table 5.5
        if DT.det_mag_neg(): # Determine if mars field
            T_mag = 0
        else:
            T_mag = DT.mag_torque(self.R_mars+h_orbit, Mag_mars, orbiter_dipole)[0]

        # Solar torque
        SA = DT.surface_area(self.params['Struct']['Orbiter radius'], self.params['Struct']['Orbiter height'])
        T_sol = DT.solar_torque(SA, Cps, Cg, i, q=0.6)

        # Gravity gradient torque
        T_gg = DT.gg_torque(orb_radius, moi, theta)

        # Aerodynamic torque
        rho = self.mars_atmos_props(h_orbit)[2]
        V = np.sqrt(self.mu_mars*(2/(self.R_mars+h_orbit) - 1/orb_radius))
        T_aero = DT.aero_torque(rho, Cd, SA, V, Cpa, Cg)

        # ID max disturbance torque
        names = ['magnetic', 'solar', 'gravity_grad', 'aerodynamic']
        torqs = [T_mag, T_sol, T_gg, T_aero]
        maxT = [0, None]
        for n, t in zip(names, torqs):
            if t > maxT[0]:
                maxT[0] = t
                maxT[1] = n

        return tuple(maxT)


if __name__ == '__main__':
    file_in = 'project/subsystems_design/AOCS/Sub_Output.xlsx'
    DP = DesignProcess(file_in)

    orb_dims = (DP.params['Struct']['Orbiter radius'], DP.params['Struct']['Orbiter radius'], DP.params['Struct']['Orbiter height'])
    prob_dims = (DP.params['Struct']['Probe radius'], DP.params['Struct']['Probe radius'], DP.params['Struct']['Probe height'])
    theta = DP.params['EPS']['max_pt_excur']  # Max excursion from nadir SC pointing

    orbiter = {'mass': 3400,        # Jun-8
               'dims': orb_dims,
               'shape': 'cylinder',
               'dipole': 0,
               'cg': 0,
               'c_pres aero': 0,
               'c_pres solar': 0,
               'solar incidence': 0,
               'pt excursion': theta,
               'Cd': 2.2}       # drag coefficient ( usually between 2 and 2.5) [SMAD]

    probe = {'mass': 130,
             'dims': prob_dims,
             'shape': 'cylinder',
             'dipole': 0,
             'cg': 0,
             'c_pres aero': 0,
             'c_pres solar': 0,
             'solar incidence': 0,
             'pt excursion': 0,
             'Cd': 2.2}         # drag coefficient ( usually between 2 and 2.5) [SMAD]


    orb_disturb_Torque = DP.id_max_torque(orbiter)
    print(orb_disturb_Torque)