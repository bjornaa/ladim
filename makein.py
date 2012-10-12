# Make an particles.in file

import numpy as np

x0, x1 = 80, 125
y0, y1 = 100, 100

Npart = 10000
#Npart = 12

Z0 = 0.0


X = np.linspace(x0, x1, Npart)
Y = np.linspace(y0, y1, Npart)

f = open('line.in', mode='w')

f.write('TR 0 hours\n')

for i in range(Npart):
    f.write("G %8.3f %8.3f %6.1f\n" % (X[i], Y[i], Z0))

f.close()
