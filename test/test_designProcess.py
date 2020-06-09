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


class TestDesignProcess(TestCase):
    def setUp(self) -> None:
        test_params = 'project/subsystems_design/AOCS/test/ref_Sub_Output.xlsx'
        self.Dsgn = DesignProcess(test_params)
        self.fireSat = {'mass': 215,
                        'dims': (1.294, 1.82998, 1.294),
                        'dipole': 0,
                        'cg': 0,
                        'c_pres aero': 0,
                        'c_pres solar': 0,
                        'solar incidence': 0,
                        'pt excursion': 1,
                        'Cd': 2.2,
                        'q': 0.6}

    @skip('Functions tested by test_disturbanceTorques.py')
    def test_id_max_torque(self):
        # skip, this gets passed by testing the individual functions
        pass

    def test_slew_torque_RW(self):
        angle = 30
        time = 10*60 # [sec]

        fs_out = self.Dsgn.slew_torque_RW(angle, time, self.fireSat)
        fs_ref = 5.2e-4

        self.assertEqual(fs_ref, round(fs_out, 5))

    def test_mom_storage_RW(self):
        TD = ('gravity_grad', 4.5e-5)


        fs_out = self.Dsgn.mom_storage_RW(TD, mu=self.Dsgn.mu_earth, planet_radius=6378)
        fs_ref = 4.7e-2

        self.assertEqual(fs_ref, round(fs_out, 3))
