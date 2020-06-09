#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
title: m_gitm
project: DSE-Mars-Reveal
date: 6/9/2020
author: lmaio
"""
import pandas as pd

gitm_path = 'data/MarsGITM/PEDE2I.MGITM.180830.UT19.userdetic.dat'

df = pd.read_csv(gitm_path)


print(df.head())