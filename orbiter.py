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
import pandas as pd

class PointMass():
    def __init__(self, mass, location, area):
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
        self.area = area


class Orbiter():
    def __init__(self, params_file):
        self.M = MarsReveal()
        self._params_file = params_file
        self.params = self.M.read_excel(self._params_file)
        self.body_dims = (self.params['Struct']['Orbiter body l'],
                          self.params['Struct']['Orbiter body w'],
                          self.params['Struct']['Orbiter body h'])
        self.pt_masses = {}

    def point_coords(self, face_comb, offset):
        loc = [0,0,0]
        l, w, h = self.body_dims
        for i, f in enumerate(face_comb):
            if f == 'x+':
                loc[0] = l/2 + offset[i]
            elif f == 'x-':
                loc[0] = -l/2 - offset[i]
            if f=='y+':
                loc[1] = w/2 + offset[i]
            elif f=='y-':
                loc[1] = -w/2 - offset[i]
            if f=='z+':
                loc[2] = h/2 + offset[i]
            elif f=='z-':
                loc[2] = -h/2 - offset[i]
        return loc

    def add_subsys_masses(self, geom_dict, **kwargs):
        for name, obj in geom_dict.items():
            mass = kwargs.get('mass', obj['mass'])
            area = kwargs.get('area', obj['area'])
            faces = [obj['face1'], obj['face2']]
            offset = [obj['offset1'], obj['offset2']]
            loc = self.point_coords(faces, offset)
            pt_mass = PointMass(mass, loc, area)

            self.pt_masses[name] = pt_mass

    def pointmass_total(self, **kwargs):
        filter = kwargs.pop('filter', '')
        mass = 0
        for n, pt in self.pt_masses.items():
            if filter in n:
                mass += pt.mass
        return mass

    def mass_breakdown(self):
        components = {}
        for n, pt in self.pt_masses.items():
            components[n] = pt.mass
        df = pd.DataFrame.from_dict(components, orient='index')
        return df

    def center_of_gravity(self, body_mass):
        total_mass = body_mass + self.pointmass_total()
        totalx = totaly = totalz = 0
        for n, pt in self.pt_masses.items():
            totalx += pt.loc[0] * pt.mass
            totaly += pt.loc[1] * pt.mass
            totalz += pt.loc[2] * pt.mass

        x = totalx / total_mass
        y = totaly / total_mass
        z = totalz / total_mass

        return x,y,z

    def pt_moment_of_inertia(self, obj, cg):
        arm = [l1 - l2 for (l1, l2) in zip(obj.loc, cg)]
        Ix = obj.mass * arm[0]**2
        Iy = obj.mass * arm[1]**2
        Iz = obj.mass * arm[2]**2
        return (Ix, Iy, Iz)

    def full_moi(self, cg, body_mass):
        moi_dict = {}
        Ix, Iy, Iz = moi_dict['body'] = self.M.sc_moment_of_inertia(body_mass, list(self.body_dims))
        for name, obj in self.pt_masses.items():
            moi = self.pt_moment_of_inertia(obj, cg)
            moi_dict[name] = moi
            Ix += moi[0]
            Iy += moi[1]
            Iz += moi[2]

        return Ix, Iy, Iz

    def center_of_pressure(self, **kwargs):
        filter = kwargs.pop('ignore_objs', [])
        max_dims = list(self.body_dims)
        max_dims.sort(reverse=True)
        tot_A = totx = toty = totz = 0


        body_A = max_dims[0]*max_dims[1]
        tot_A += body_A

        for name, obj in self.pt_masses.items():
            if not np.isnan(obj.area) and name not in filter:
                tot_A += obj.area
                totx += obj.area * obj.loc[0]
                toty += obj.area * obj.loc[1]
                totz += obj.area * obj.loc[2]

        x = totx / tot_A
        y = toty / tot_A
        z = totz / tot_A
        return (x,y,z), tot_A

    def vehicle_props(self, total_mass, **kwargs):
        geo_file = 'project/subsystems_design/AOCS/geometry.xlsx'
        prop = self.params['Prop']

        geom_columns = ['name', 'face1', 'face2', 'offset1', 'offset2', 'mass', 'area']
        geom = self.M.read_excel(geo_file, sheet_name=['Thrusters', 'TTC', 'Fuel', 'EPS'], columns=geom_columns)

        # Add thrusters
        self.add_subsys_masses(geom['Thrusters'], mass=prop['Maintenance thruster mass'])

        att_thrust_mass = self.pointmass_total(filter='att')
        prop_sys_mass = prop['Circularisation propulsion system dry mass'] + prop[
            'Maintenance fuel mass']  # +prop['Circularisation fuel mass']

        # Add propellant tanks
        self.add_subsys_masses(geom['Fuel'], mass=(prop_sys_mass - att_thrust_mass) / 4)

        # Add TTC
        self.add_subsys_masses(geom['TTC'])

        # Add Solar Array
        self.add_subsys_masses(geom['EPS'])

        #### Compute remaining body mass
        component_mass = self.pointmass_total()
        central_lump_mass = total_mass - component_mass

        # mass_breakdown = O.mass_breakdown()
        cg = self.center_of_gravity(central_lump_mass)

        # Moment of inertia calc
        moi = self.full_moi(cg, central_lump_mass)

        # Center of pressure aero
        aero_ignore = kwargs.pop('aero_ignore', [])
        cp_ae, SA_aero = self.center_of_pressure(ignore_objs=aero_ignore)

        # Center of pressure solar
        cp_sol, SA_solar = self.center_of_pressure()

        new_props = {'mass': total_mass,  # Jun-8
                     'cg': cg,
                     'c_pres aero': cp_ae,
                     'c_pres solar': cp_sol,
                     'aero surface area': SA_aero,
                     'solar surface area': SA_solar,
                     'moi': moi}

        return new_props



if __name__ == '__main__':
    params_file = 'project/subsystems_design/AOCS/Sub_Output.xlsx'
    geo_file = 'project/subsystems_design/AOCS/geometry.xlsx'

    O = Orbiter(params_file)
    on_station_mass = 516.39  # Jun-9

    veh_props = O.vehicle_props(on_station_mass)
    print(veh_props)