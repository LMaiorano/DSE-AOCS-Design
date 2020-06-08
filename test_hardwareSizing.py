#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
title: test_hardwareSizing
project: DSE-Mars-Reveal
date: 6/8/2020
author: lmaio
"""
from unittest import TestCase
from project.subsystems_design.AOCS.AOCS_sizing_models import HardwareSizing


class TestHardwareSizing(TestCase):
    def setUp(self) -> None:
        test_params = 'project/subsystems_design/AOCS/test/ref_Sub_Output.xlsx'
        self.HW = HardwareSizing(test_params)


    def test_orbiter_moi_rough_max(self):
        self.fail()

    def test_slew_torque_RW(self):
        self.fail()
