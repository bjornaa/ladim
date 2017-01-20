# Make an particles.in file

import numpy as np

# End points of line in grid coordinates
x0, x1 = 80, 125
y0, y1 = 100, 100

# Number of particles along the line
Npart = 8000

# Fixed particle depth
Z = 0.0    

X = np.linspace(x0, x1, Npart)
Y = np.linspace(y0, y1, Npart)

f = open('line.in', mode='w')

for i, (x, y) in enumerate(zip(X, Y)):
    f.write('1 1989-05-24T12 {:7.3f} {:7.3f} {:6.1f}\n'.format(x, y, Z))

f.close()
