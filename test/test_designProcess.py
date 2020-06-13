#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
title: test_designProcess
project: DSE-Mars-Reveal
date: 6/8/2020
author: lmaio
"""
from unittest import TestCase, skip
from project.subsystems_design.AOCS.AOCS_design_process import DesignProcess
from project.subsystems_design.AOCS.vehicle import Orbiter
from definitions import MarsReveal


class TestDesignProcess(TestCase):
    def setUp(self) -> None:
        ref_sub_output = 'project/subsystems_design/AOCS/test/ref_Sub_Output.xlsx'
        ref_des_params = 'project/subsystems_design/AOCS/test/desgn_params_VV.xlsx'
        ref_geomety = 'project/subsystems_design/AOCS/test/geometry_VV.xlsx'

        # Orbiter Vehicle
        self.O = Orbiter(ref_sub_output, ref_des_params)

        self.O.vehicle_props(geometry_file=ref_geomety)  # compute vehicle properties

        self.M = MarsReveal()

        # ---- Design object -------
        self.Dsgn = DesignProcess(ref_sub_output, ref_des_params, self.O.props)

        # Parameters
        self.fireSat = self.O.M.read_excel('project/subsystems_design/AOCS/test/props_dump.xlsx',
                                           sheet_name='dump_props')
        self.fireSat['moi'] = (90, 60, 90)
        self.mu = 3.986e14
        self.R_earth = 6378

    def test_id_max_torque(self):
        # self.O.M.save_excel(self.O.props, 'project/subsystems_design/AOCS/test/props_dump.xlsx', 'dump_props')
        max_external_torque = self.Dsgn.worst_torque(self.fireSat,
                                                     planet_mag_field=7.96e15,
                                                     planet_radius=self.R_earth,
                                                     solar_const=1367,
                                                     mu=self.mu,
                                                     rho=1e-13,
                                                     V=7504)[0]

        ref_max_T = 4.5e-5
        self.assertEqual(ref_max_T, round(max_external_torque[1], 6))

    def test_slew_torque_RW(self):
        fs_out = self.Dsgn.slew_torque_RW(self.Dsgn.mission, moi=self.fireSat['moi'], seconds=600)
        fs_ref = 5.2e-4

        self.assertEqual(fs_ref, round(fs_out, 5))

    def test_mom_storage_RW(self):
        TD = ('gravity_grad', 4.5e-5)

        fs_out = self.Dsgn.mom_storage_RW(TD, orb_period=5928, mu=self.Dsgn.M.mu_earth, planet_radius=self.R_earth)
        fs_ref = 4.7e-2

        self.assertAlmostEqual(fs_out, fs_ref, 3)

    def test_mom_storage_for_accuracy_in_MW(self):
        TD = ('gravity_grad', 4.5e-5)

        fs_out = self.Dsgn.mom_storage_for_accuracy_in_MW(TD, accuracy=0.1, mu=3.986e5, planet_radius=self.R_earth)
        fs_ref = 38.2

        self.assertAlmostEqual(fs_ref, fs_out, 1)

    def test_thrust_force_disturbances(self):
        TD = ('gravity_grad', 4.5e-5)

        fs_out = self.Dsgn.thrust_force_disturbances(TD, L=0.5)
        fs_ref = 9e-5

        self.assertAlmostEqual(fs_ref, fs_out, 6)

    def test_thrust_force_slewing(self):
        L = 0.5

        fs_out = self.Dsgn.thrust_force_slewing(self.Dsgn.mission, L=L, moi=self.fireSat['moi'])
        fs_ref = 0.52

        self.assertAlmostEqual(fs_out, fs_ref, 2)

    def test_thrust_force_momentum_dump(self):
        stored_momentum = 0.4
        arm = 0.5
        burn_time = 1

        fs_out = self.Dsgn.thrust_force_momentum_dump(stored_momentum, burn_time, L=arm)
        fs_ref = 0.8

        self.assertAlmostEqual(fs_ref, fs_out, 1)

    def test_thruster_pulse_life(self):
        fs_out = self.Dsgn.thruster_pulse_life(self.Dsgn.mission)[0]
        fs_ref = 5715

        self.assertEqual(fs_out, fs_ref)

    def test_propellent_mass(self):
        pulses = (240, 5475)
        mom_dump_thrust = 0.8
        slew_thrust = 0.52

        fs_out = self.Dsgn.propellent_mass(self.Dsgn.mission, pulses, slew_thrust, mom_dump_thrust, g_planet=9.8)
        fs_ref = 2.43

        self.assertAlmostEqual(fs_ref, fs_out, 2)
