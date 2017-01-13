#! /usr/bin/env python
# -*- coding: utf-8 -*-

# import numpy as np
from netCDF4 import num2date
from trackpart import Euler_Forward
from input import ROMS_input
from release import ParticleReleaser
from ladim_config import Configure
from ladim_state import State
from output import OutPut
from behaviour import behaviour

# ==================
# Initiate the model
# ==================

# Read the configuration file
# --------------------

config_file = 'ladim.yaml'      # take from command line

print(" --- pyladim configuration ----")
config = Configure(config_file)
print("configuration file: ", config_file)
config.write()
print(" --- end of configuration ---\n")

nsteps = config.nsteps
dt = config.dt


# State
state = State(config)

# --------------------
# Input grid and files
# --------------------

inp = ROMS_input(config)

tunits = inp.nc.variables['ocean_time'].units

# ----------------------
# Particle release file
# ----------------------

partini = ParticleReleaser(config)
# partini.scan()   # Gjør dette til del av __init__

# ------------------
# Init output file
# -----------------

out = OutPut(config)

# ==============
# Main time loop
# ==============

print(type(nsteps))
for i in range(nsteps+1):
    inp.update(i)

    # Read particles ?
    if i in partini.release_steps:
        # Tips: Gjøre begge delet i read_particles
        V = next(partini)
        state.append(V)

    # Save to file
    if i % config.output_period == 0:
        print("i = ", i, num2date(i*dt,
              'seconds since %s' % str(config.start_time)))
        out.write(state)

    # Only use surface forcing presently
    # Redundant to give both inp, and inp.U ...
    Euler_Forward(inp, inp.U, inp.V, state.X, state.Y, state.Z, dt=dt)

    # Behaviour
    behaviour(state)


# ========
# Clean up
# ========

inp.close()
out.close()
