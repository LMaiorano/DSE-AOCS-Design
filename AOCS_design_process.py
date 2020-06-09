#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
title: AOCS_iterations
project: DSE-Mars-Reveal
date: 6/8/2020
author: lmaio
"""
import numpy as np
from project.subsystems_design.AOCS.AOCS_sizing_models import DisturbanceTorques
from project.subsystems_design.AOCS.orbiter import Orbiter
from definitions import MarsReveal

class DesignProcess(MarsReveal):
    def __init__(self, params_file):
        super().__init__()
        self.params_file = params_file
        self.params = self.read_excel(self.params_file)
        self.h_orbit = self.params['Astro']['h']


    def id_max_torque(self, veh_props, **kwargs):
        DT = DisturbanceTorques(self.params_file)
        planet_radius = kwargs.pop('planet_radius', self.R_mars)

        orb_radius = planet_radius + self.h_orbit



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
        # moi = self.sc_moment_of_inertia(veh_props['mass'], veh_props['dims'])

        moi = veh_props['moi']
        # Magnetic torque
        magn_mars = (5 * 10 ** -8) * (3397 ** 3) / 2  # [T km^3] from Elements of S/c Engineering, Table 5.5
        planet_magnetic = kwargs.pop('planet_mag_field', magn_mars)

        if DT.det_mag_neg(): # Determine if mars field will have negligible effect
            T_mag = 0
        else:
            T_mag = DT.mag_torque(planet_radius+self.h_orbit, planet_magnetic, orbiter_dipole)[0]

        # Solar torque
        # SA = DT.surface_area(veh_props['dims'])
        SA = veh_props['surface area']
        T_sol = DT.solar_torque(SA, Cps, Cg, i, q=0.6)

        # Gravity gradient torque
        T_gg = DT.gg_torque(orb_radius, moi, theta)

        # Aerodynamic torque
        rho = self.mars_atmos_props(self.h_orbit)[2]
        V = np.sqrt(self.mu_mars*(2/(self.R_mars+self.h_orbit) - 1/orb_radius))
        T_aero = DT.aero_torque(rho, Cd, SA, V, Cpa, Cg)

        # ID max disturbance torque
        names = ['magnetic', 'solar', 'gravity_grad', 'aerodynamic']
        torqs = [T_mag, T_sol, T_gg, T_aero]
        maxT = [None, 0]
        for n, t in zip(names, torqs):
            if t > maxT[1]:
                maxT[1] = t
                maxT[0] = n

        return tuple(maxT)




    def slew_torque_RW(self, angle, seconds, veh_props):
        '''Calculates torque for max-acceleration slew operations

        Args:
            angle: float
                slew requirement [deg]
            time: float
                slew time requirement [sec]
            veh_props: dict

        Returns:

        '''
        moi = self.sc_moment_of_inertia(veh_props['mass'], veh_props['dims'])
        I = max(moi)

        slew_torq = 4 * np.radians(angle) * I / (seconds**2)
        return slew_torq


    def mom_storage_RW(self, worst_torque, **kwargs):
        '''Integrates worst-case (cyclic) disturbance torque over a full orbit.
        Necessary to estimate RW momentum storage

        Args:
            worst_torque: tuple
                worst-case disturbance torque (name, torque)

        Returns:

        '''
        # Name options ['magnetic', 'solar', 'gravity_grad', 'aerodynamic']
        mu = kwargs.pop('mu', self.mu_mars)
        planet_radius = kwargs.pop('planet_radius', self.R_mars)
        name, T = worst_torque

        orb_radius = planet_radius + self.h_orbit
        orb_period = 2 * np.pi * np.sqrt(orb_radius ** 3 / mu)

        if name in ['magnetic', 'solar']:
            # half cyclic
            h = T * orb_period / 2 *0.707
        elif name == 'gravity_grad':
            # quarter cyclic
            h = T * orb_period / 4 *0.707
        else:
            # secular
            h = T * orb_period
        return h



if __name__ == '__main__':
    file_in = 'project/subsystems_design/AOCS/Sub_Output.xlsx'
    Design = DesignProcess(file_in)

    orb_dims = (Design.params['Struct']['Orbiter radius'], Design.params['Struct']['Orbiter height']) # FIXME: should be box
    prob_dims = (Design.params['Struct']['Probe radius'], Design.params['Struct']['Probe height'])
    theta = Design.params['EPS']['max_pt_excur']  # Max excursion from nadir SC pointing

    O = Orbiter(file_in)
    orb_on_station_mass = 516.39  # Jun-9

    orbiter_props = O.vehicle_props(orb_on_station_mass)
    orbiter = {'dipole': 0,
               'solar incidence': 0,
               'pt excursion': theta,
               'Cd': 2.2,
               'q': 0.6}       # drag coefficient ( usually between 2 and 2.5) [SMAD]

    for param, val in orbiter_props.items():
        orbiter[param] = val


    probe = {'mass': 130,
             'dims': prob_dims,
             'dipole': 0,
             'cg': 0,
             'c_pres aero': 0,
             'c_pres solar': 0,
             'solar incidence': 0,
             'pt excursion': 0,
             'Cd': 2.2,
             'q': 0.6}         # drag coefficient ( usually between 2 and 2.5) [SMAD]


    orb_max_disturb = Design.id_max_torque(orbiter) # [N m]

    mom_storage = Design.mom_storage_RW(orb_max_disturb) #[N m s]


    # Write to output
    # Create separate output dictionary, to prevent accidental mix of in/outputs
    out_params = Design.read_excel(file_in, sheet_name='AOCS')

    # Modify values to the new calculated outputs
    out_params['orb_max_disturb_torque'] = list(orb_max_disturb)[1]
    out_params['orb_max_disturb_name'] = list(orb_max_disturb)[0]
    out_params['orb_momentum_storage'] = mom_storage

    # Save Values
    Design.save_excel(out_params, file_in, 'AOCS')
    print(orb_max_disturb)