#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
title: AOCS_iterations
project: DSE-Mars-Reveal
date: 6/8/2020
author: lmaio
"""
import numpy as np
from project.subsystems_design.AOCS.AOCS_disturb_torques import DisturbanceTorques
from project.subsystems_design.AOCS.orbiter import Orbiter
from definitions import MarsReveal

class DesignProcess():
    def __init__(self, params_file, veh_props):
        # super().__init__()
        self.params_file = params_file
        self.M = MarsReveal()
        self.params = self.M.read_excel(self.params_file)
        self.h_orbit = self.params['Astro']['h']
        self.veh = veh_props


    def worst_torque(self, veh_props, **kwargs):
        DT = DisturbanceTorques(self.params_file)
        planet_radius = kwargs.pop('planet_radius', self.M.R_mars)

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
        SA_sol = veh_props['solar surface area']
        T_sol = DT.solar_torque(SA_sol, Cps, Cg, i, q=0.6)

        # Gravity gradient torque
        T_gg = DT.gg_torque(orb_radius, moi, theta)

        # Aerodynamic torque
        SA_aero = veh_props['aero surface area']
        self.rho = self.M.mars_atmos_props(self.h_orbit*10**3)[2]
        self.V = np.sqrt(self.M.mu_mars*(2/(self.M.R_mars+self.h_orbit) - 1/orb_radius))
        T_aero, Drag_aero = DT.aero_torque(self.rho, Cd, SA_aero, self.V, Cpa, Cg)

        # ID max disturbance torque
        names = ['magnetic', 'solar', 'gravity_grad', 'aerodynamic']
        torqs = [T_mag, T_sol, T_gg, T_aero]
        maxT = [None, 0]
        for n, t in zip(names, torqs):
            if t > maxT[1]:
                maxT[1] = t
                maxT[0] = n

        return tuple(maxT), Drag_aero, torqs

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
        # moi = self.M.sc_moment_of_inertia(veh_props['mass'], veh_props['dims'])
        moi = veh_props['moi']
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

        mu = kwargs.pop('mu', self.M.mu_mars)
        planet_radius = kwargs.pop('planet_radius', self.M.R_mars)
        name, T = worst_torque

        orb_radius = planet_radius + self.h_orbit
        self.orb_period = 2 * np.pi * np.sqrt(orb_radius ** 3 / mu)

        # Name options ['magnetic', 'solar', 'gravity_grad', 'aerodynamic']
        if name in ['magnetic', 'solar']:
            # half cyclic
            h = T * self.orb_period / 2 *0.707
        elif name == 'gravity_grad':
            # quarter cyclic
            h = T * self.orb_period / 4 *0.707
        else:
            # secular
            h = T * self.orb_period
        return h

    def mom_storage_for_accuracy_in_MW(self, worst_torque, accuracy, **kwargs):
        '''
        Args:
            worst_torque:
                worst_torque [N m]
            accuracy:
                pointing accuracy [deg]
            **kwargs:

        Returns:

        '''
        mu = kwargs.pop('mu', self.M.mu_mars)
        name, T = worst_torque

        planet_radius = kwargs.pop('planet_radius', self.M.R_mars)
        orb_radius = planet_radius + self.h_orbit
        orb_period = 2 * np.pi * np.sqrt(orb_radius ** 3 / mu)

        h = T * (orb_period/4) / (np.radians(accuracy))

        return h

    def _worst_thrust_couple(self) -> list:
        '''Id thruster couple with worst moment arm pair from calculated cg
        pair-wise found as follows: att1 - att3
        '''
        min_couple = ['none', float('inf')]
        objs = self.veh['pt masses']
        thrs = [n for n in objs.keys() if 'att' in n]

        for att in thrs:
            pair = objs[att].t_pair
            thrs.remove(pair)
            att_T = np.cross(objs[att].t_arm, objs[att].t_vect)
            pair_T = np.cross(objs[pair].t_arm, objs[pair].t_vect)


            tot_T_mag = np.linalg.norm(att_T) + np.linalg.norm(pair_T)
            if tot_T_mag < min_couple[1]:
                min_couple = [att, tot_T_mag]

        return min_couple

    def _shortest_effective_thrust_arm(self):
        worst_couple = self._worst_thrust_couple()[0]
        att = self.veh['pt masses'][worst_couple]
        pr = self.veh['pt masses'][att.t_pair]

        arms = []
        for th in [att, pr]:
            # mask arm array to exclude arm to axis parallel with thrust vector
            mask = 1 - np.abs(th.t_vect)
            masked = np.abs(np.multiply(th.t_arm,  mask))
            arms.append(masked.max())

        return sum(arms)


    def thrust_force_disturbances(self, worst_torque):
        '''Min total thrust force of a couple for worst disturbance torque
            Uses shortest (worst case) thruster arm to cg or sizing (1D)
        Returns: [N] minimum required thrust
        '''
        L = self._shortest_effective_thrust_arm()
        F = worst_torque[1]/L
        return F

    def thrust_force_slewing(self, profile):
        angle, seconds = profile['slew_angle'], profile['slew_time']

        L = self._shortest_effective_thrust_arm()
        rate = angle/seconds # [deg/sec]
        accel_t = seconds * profile['slew_burn_pct'] # [sec]
        accel = rate/ accel_t # [deg/sec^2]

        moi = self.veh['moi']
        F = max(moi) * accel / L
        return F


    def thrust_force_momentum_dump(self, stored_momentum, burn_time):
        '''Uses shortest (worst case) thruster arm to cg or sizing (1D)
        Args:
            stored_momentum: [N m s]
            burn_time: [s]
        '''
        L = self._shortest_effective_thrust_arm()
        F = stored_momentum / (L * burn_time)
        return F

    def secular_momentum(self, mission):
        orb_p_dump = 60 * 60 * 24 / Design.orb_period / mission['mom_dump_freq']  # number orbits per momentum dump
        orb_aero_T = self.worst_torque(self.veh)[2][3]
        return orb_aero_T*orb_p_dump

    def thruster_pulse_life(self, pulse_profile):
        pp = pulse_profile
        slew_pulses = 2 * pp['n_slew_axes'] * pp['n_slew_maneuvers']
        mom_pulses = 1 * 3 * 365 * pp['mom_dump_freq'] * pp['lifetime']
        tot_pulses = mom_pulses + slew_pulses
        return tot_pulses, (slew_pulses, mom_pulses)


    def propellent_mass(self, profile, pulses, slewF, momF):
        s_puls, m_puls = pulses
        Isp = self.params['Prop']['Maintenance Isp']
        tot_imp = s_puls * profile['slew_burn_pct']*profile['slew_time'] * slewF \
                  + m_puls*profile['burn_time']*momF

        m_prop = tot_imp/(Isp * self.M.g_earth)
        return m_prop





if __name__ == '__main__':
    file_in = 'project/subsystems_design/AOCS/Sub_Output.xlsx'
    AOCS_mission = 'project/subsystems_design/AOCS/mission_profile.xlsx'

    O = Orbiter(file_in)
    orb_on_station_mass = 516.39  # Jun-9
    aerodyn_ignore = []#['sa1', 'sa2']#, 'TTC-earth'] # Objects to ignore for aerodynamic cp calculations

    orbiter_props = O.vehicle_props(orb_on_station_mass, aero_ignore=aerodyn_ignore)
    orbiter = {'dipole': 0,
               'solar incidence': 0,
               'pt excursion': 23.5, #eps
               'Cd': 2.2,
               'q': 0.6,
               'pt accuracy': .5}  # drag coefficient ( usually between 2 and 2.5) [SMAD]

    for param, val in orbiter_props.items():
        orbiter[param] = val

    # ---- Design object -------
    Design = DesignProcess(file_in, orbiter)
    mission = Design.M.read_excel(AOCS_mission, sheet_name='orbiter', columns=['name', 'value'])

    # orb_dims = (Design.params['Struct']['Orbiter radius'], Design.params['Struct']['Orbiter height']) # FIXME: should be box
    # prob_dims = (Design.params['Struct']['Probe radius'], Design.params['Struct']['Probe height'])
    # theta = Design.params['EPS']['max_pt_excur']  # Max excursion from nadir SC pointing





    # probe = {'mass': 130,
    #          'dims': prob_dims,
    #          'dipole': 0,
    #          'cg': 0,
    #          'c_pres aero': 0,
    #          'c_pres solar': 0,
    #          'solar incidence': 0,
    #          'pt excursion': 0,
    #          'Cd': 2.2,
    #          'q': 0.6}         # drag coefficient ( usually between 2 and 2.5) [SMAD]


    # ------ Start sizing --------



    orb_max_disturb, drag, _ = Design.worst_torque(orbiter) # [N m]

    mom_storage = Design.mom_storage_RW(orb_max_disturb) #[N m s]


    mom_wheel_accuracy = Design.mom_storage_for_accuracy_in_MW(orb_max_disturb, orbiter['pt accuracy'])

    # Thruster sizing TODO: Check with probes onboard
    th_dist_torque = Design.thrust_force_disturbances(orb_max_disturb)

    th_slew_maneuver = Design.thrust_force_slewing(mission)

    mom_buildup = Design.secular_momentum(mission)
    th_mom_dump = Design.thrust_force_momentum_dump(mom_buildup, mission['burn_time'])

    life_pulses, pulses = Design.thruster_pulse_life(mission)

    prop_mass = Design.propellent_mass(mission, pulses, th_slew_maneuver, th_mom_dump)







    # --------------- Write to output ---------------------
    # Create separate output dictionary, to prevent accidental mix of in/outputs
    out_params = Design.M.read_excel(file_in, sheet_name='AOCS')

    # Modify values to the new calculated outputs
    out_params['orb_max_disturb_torque'] = list(orb_max_disturb)[1]
    out_params['orb_max_disturb_type'] = list(orb_max_disturb)[0]
    out_params['orb_momentum_storage'] = mom_storage
    out_params['ignored mass bodies'] = aerodyn_ignore
    out_params['aero drag'] = drag
    out_params['thruster pulses'] = life_pulses
    out_params['min thrust momentum dump'] = th_mom_dump
    out_params['min thrust slew'] = th_slew_maneuver
    out_params['O RCS fuel'] = prop_mass

    # Save Values
    Design.M.save_excel(out_params, file_in, 'AOCS')
    # print(orb_max_disturb)