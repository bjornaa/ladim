# Classes for Particle and State variables

import sys
import os
import importlib
import logging
from typing import Any, Dict, Sized     # mypy

import numpy as np
from .tracker import Tracker
from .gridforce import Grid, Forcing

# ------------------------

Config = Dict[str, Any]


class State(Sized):
    """The model variables at a given time"""

    def __init__(self, config: Config) -> None:
        """Initialize an empty initial state"""

        logging.info("Initializing the model state")

        self.timestep = 0
        self.timestamp = config['start_time'].astype('datetime64[s]')
        self.dt = np.timedelta64(config['dt'], 's')
        self.position_variables = ['X', 'Y', 'Z']
        # self.ibm_variables = config['ibm_variables']
        self.state_variables = config['state_variables']
        self.particle_variables = config['particle_variables']
        # Can there be state variables that are not instance variables
        self.instance_variables = [var for var in self.state_variables
                                   if var not in self.particle_variables]
        # reserved_variables = ['pid', 'X', 'Y', 'Z', 'lon', 'lat']

        # pid is integer, rest = float
        # Kan ha andre heltall, f.eks. stadie nummer
        # Generalisere til dict: var -> type?
        self.pid = np.array([], dtype=int)
        for name in (set(self.instance_variables) - {'pid'}):
            setattr(self, name, np.array([], dtype=float))

        for name in self.particle_variables:
            setattr(self, name,
                    np.array([], dtype=config['release_dtype'][name]))

        self.track = Tracker(config)
        self.dt = config['dt']

        if config['ibm_module']:
            # Import the module
            logging.info("Initializing the IBM")
            sys.path.insert(0, os.getcwd())
            ibm_module = importlib.import_module(config['ibm_module'])
            # Initiate the IBM object
            self.ibm = ibm_module.IBM(config)
        else:
            self.ibm = None

        # self.num_particles = len(self.X)
        self.nnew = 0

    def __getitem__(self, name: str) -> None:
        return getattr(self, name)

    def __setitem__(self, name: str, value: Any) -> None:
        return setattr(self, name, value)

    def __len__(self) -> int:
        return len(getattr(self, 'X'))

    def append(self, new: Dict[str, Any], grid: Grid) -> None:
        """Append new particles to the model state"""
        nnew = len(new['pid'])
        logging.debug(f"Appending {nnew} particles")
        # self.pid = np.concatenate((self.pid, new['pid']))
        for name in self.instance_variables:
            if name in new:
                self[name] = np.concatenate((self[name], new[name]))
            else:   # Initialize to zero
                self[name] = np.concatenate((self[name], np.zeros(nnew)))
        self.nnew = nnew

        if 'lon' in self.instance_variables:
            self.lon, self.lat = grid.lonlat(self['X'], self['Y'])

    def update(self, grid: Grid, forcing: Forcing) -> None:
        """Update the model state to the next timestep"""

        # From physics all particles are alive
        self.alive = np.ones(len(self), dtype='bool')

        self.timestep += 1
        self.timestamp += np.timedelta64(self.dt, 's')
        self.track.move_particles(grid, forcing, self)
        # logging.info(
        #        "Model time = {}".format(self.timestamp.astype('M8[h]')))
        if self.timestamp.astype('int') % 3600 == 0:     # New hour
            logging.info(
                "Model time = {}".format(self.timestamp.astype('M8[h]')))

        # Longitude/latitutde
        # If not used by IBM, may not be necessary except at output
        if 'lon' in self.instance_variables:
            self.lon, self.lat = grid.lonlat(self['X'], self['Y'])

        # Update the IBM
        if self.ibm:
            self.ibm.update_ibm(grid, self, forcing)

        # Surface/bottom boundary conditions
        #     Reflective  at surface
        cond = self.Z < 0
        self.Z[cond] = - self.Z[cond]
        #     Keep just above bottom
        H = grid.sample_depth(self['X'], self['Y'])
        cond = self.Z > H
        self.Z[cond] = 0.99*H[cond]

        # Compactify by removing dead particles
        # Could have a switch to avoid this if no deaths
        # self.pid = self.pid[self.alive]
        for key in self.instance_variables:
            self[key] = self[key][self.alive]
