#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
title: test_disturbanceTorques
project: DSE-Mars-Reveal
date: 6/8/2020
author: lmaio
"""
from unittest import TestCase
from project.subsystems_design.AOCS.AOCS_disturb_torques import DisturbanceTorques


class TestDisturbanceTorques(TestCase):
    '''All tests based on SMAD FireSat Example'''
    def setUp(self) -> None:
        test_params = 'project/subsystems_design/AOCS/test/ref_Sub_Output.xlsx'
        self.DT = DisturbanceTorques(test_params)
        self.fireSat = {'mass': 215,
                        'dims': (1.294, 1.82998, 1.294),
                        'dipole': 0,
                        'cg': 0,
                        'c_pres aero': 0,
                        'c_pres solar': 0,
                        'solar incidence': 0,
                        'pt excursion': 1,
                        'Cd': 2.2}


    def test_mag_torque(self):
        R = 7078
        M = 7.96e15
        D = 1

        fs_out = self.DT.mag_torque(R, M, D)[0]
        fs_ref = 4.5e-5

        self.assertEqual(fs_ref, round(fs_out, 6))


    def test_solar_torque(self):
        solar_irr = 1367
        q = 0.6
        As = 2 * 1.5
        Cps = 0.3
        cg = 0
        i = 0

        fs_out = self.DT.solar_torque(As, Cps, cg, i, q, solar_const=solar_irr)
        fs_ref = 6.6e-6

        self.assertEqual(fs_ref, round(fs_out, 7))

    def test_gg_torque(self):
        R = 7078.0
        theta = 1
        moi = (90, 60, 90)
        mu_earth = 3.986e14

        fs_out = self.DT.gg_torque(R, moi, theta, mu=mu_earth)
        fs_ref = 1.8e-6

        self.assertEqual(round(fs_out, 7), fs_ref)


    def test_aero_torque(self):
        A = 3
        Cpa = 0.2
        cg = 0
        V = 7504
        rho = 1e-13
        Cd = 2

        fs_out,  _= self.DT.aero_torque(rho, Cd, A, V, Cpa, cg)
        fs_ref = 3.4e-6

        self.assertEqual(fs_ref, round(fs_out, 7))
