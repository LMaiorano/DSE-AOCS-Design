#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
title: orbiter
project: DSE-Mars-Reveal
date: 6/9/2020
author: lmaio
"""
from definitions import MarsReveal
import numpy as np

class PointMass():
    def __init__(self, mass, location):
        '''
        Args:
            dims: (l, w, h)
                l -> x-axis
                w -> y-axis
                z -> z-axis
            mass: kg
            location: (x, y, z)
        '''
        self.mass = mass
        self.loc = location


class Orbiter():
    def __init__(self, params_file):
        self.M = MarsReveal()
        self.params_file = params_file
        self.params = self.M.read_excel(self.params_file)
        self.body_dims = (self.params['Struct']['Orbiter body l'],
                          self.params['Struct']['Orbiter body w'],
                          self.params['Struct']['Orbiter body h'])
        self.thrusters = {}

    def point_coords(self, face_comb, offset):
        loc = [0,0,0]
        l, w, h = self.body_dims
        for i, f in enumerate(face_comb):
            if f == 'x+':
                loc[0] = l/2 + offset[i]
            elif f == 'x-':
                loc[0] = -l/2 + offset[i]
            if f=='y+':
                loc[1] = w/2 + offset[i]
            elif f=='y-':
                loc[1] = -w/2 + offset[i]
            if f=='z+':
                loc[2] = h/2 + offset[i]
            elif f=='z-':
                loc[2] = -h/2 + offset[i]
        return loc

    def add_thruster(self, label, obj):
        self.thrusters[label] = obj



if __name__ == '__main__':
    params_file = 'project/subsystems_design/AOCS/Sub_Output.xlsx'
    geo_file = 'project/subsystems_design/AOCS/geometry.xlsx'

    O = Orbiter(params_file)

    geom = O.M.read_excel(geo_file, sheet_name=['Thrusters', 'TTC'], columns=['name', 'face1', 'face2', 'offset1', 'offset2'])
    # Add thrusters
    for i, th in geom['Thruster'].items():
        mass = O.params['Prop']['Maintenance thruster mass']
        faces = [th['face1'], th['face2']]
        offset = [0,0]
        loc = O.point_coords(faces, offset)
        thruster = PointMass(mass, loc)

        O.add_thruster(i, thruster)

    print('end')