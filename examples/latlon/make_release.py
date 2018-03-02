# Make a release file for instantaneous release along 59 degN

# Uses the ll2xy method of the Grid class in the gridforce module
# to convert from lon/lat to grid coordinates

import numpy as np
from netCDF4 import Dataset
from ladim.gridforce.ROMS import Grid

# Grid file
grid_file = '../data/ocean_avg_0014.nc'

# End points of line, lon, lat
lon0, lat0 = -2.5, 59.0
lon1, lat1 =  5.2, 59.0

# Number of particles along the line
Npart = 500

# Constant particle depth
Z = 5

# Geographical positions along line
lon = np.linspace(lon0, lon1, Npart)
lat = np.linspace(lat0, lat1, Npart)

# Compute grid coordinates
config = dict(grid_file=grid_file, grid_args=[])
grd = Grid(config)
X, Y = grd.ll2xy(lon, lat)

# Write to release file
with open('latlon.rls', mode='w') as f:
    for (x, y) in zip(X, Y):
        f.write(f'1989-05-24T12 {x:7.3f} {y:7.3f} {Z:6.1f}\n')
