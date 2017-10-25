# Make an particles.in file

import numpy as np

# End points of line in grid coordinates
x0, x1 = 68, 123
x0, x1 = 67.55, 123.45
x0, x1 = 66.55, 123.45
y0, y1 = 95, 90
y0, y1 = 93.4, 90



# Number of particles along the line
Npart = 1000

# Fixed particle depth
Z = 5

X = np.linspace(x0, x1, Npart)
Y = np.linspace(y0, y1, Npart)

f = open('line.rls', mode='w')

for i, (x, y) in enumerate(zip(X, Y)):
    if i < 500:
        nat = 'Scotland'
    else:
        nat = 'Norway'
    f.write('1989-05-24T12 {:7.3f} {:7.3f} {:6.1f} {:s}\n'.
             format(x, y, Z, nat))

f.close()
