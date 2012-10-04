# -*- coding: utf-8 -*-

# Particle release class


import numpy as np

class ParticleReleaser(object):

    def __init__(self, particle_release_file, dt):
        
        self.dt = dt   # Finne annen måte å få tak i denne setup-info?

        # Open the file and init counters
        self.fid = open(particle_release_file)
        self.particle_counter = 0
        self.release_step = 0
        
        # Init empty particle release values
        self._pid, self._start = [], []
        self._X, self._Y, self._Z  = [], [], []
        self.pid   = np.array(self._pid, dtype='int')
        self.X     = np.array(self._X, dtype='float32')
        self.Y     = np.array(self._Y, dtype='float32')
        self.Z     = np.array(self._Z, dtype='float32')
        self.start = np.array(self._start, dtype='int')

        # Read until first time line
        for line in self.fid:
            if line[0] == 'T' : break

    # ------

    def read_particles(self):  # Leser til neste "T"

        #for line in self.fid:
        while 1:
            try:
                line = self.fid.next()
            except StopIteration:
                print "==>  end of file"

                # Save last array versions of the accumultators
                self.pid   = np.array(self._pid)
                self.X     = np.array(self._X)
                self.Y     = np.array(self._Y)
                self.Z     = np.array(self._Z)
                self.start = np.array(self._start)
                # Indicate end of file by impossible value for release_step
                self.release_step = -99  
                break
            

            # Remove trailing white space
            line = line.strip()  

            # Skip blank lines
            if not line: continue

            # Skip comments
            if line[0] in ['#','!']: continue
            
            if line[0] == 'G':   # Grid coordinates
                self.particle_counter += 1   # New particle

                # Add particle characteristics to accumulators
                w = line.split()
                self._pid.append(self.particle_counter)
                self._X.append(float(w[1]))
                self._Y.append(float(w[2]))
                self._Z.append(float(w[3]))
                self._start.append(self.release_step)
                 
            if line[0] == "T": # Time line

                # Make arrays of the accumulators
                self.pid   = np.array(self._pid)
                self.X     = np.array(self._X)
                self.Y     = np.array(self._Y)
                self.Z     = np.array(self._Z)
                self.start = np.array(self._start)

                # Next release step
                if line[1] == "R":  # Relative time
                    w = line.split()
                    tdelta = int(w[1])
                    units = w[2]
                    if units[0] == 'h':
                        tdelta = tdelta*3600
                    elif units[0] == 'd': 
                        tdelta = tdelta*24*3600
                    self.release_step = tdelta // self.dt
                    #print "next release step = ", release_step

                # Initialise accumulators for next step
                self._pid, self._start = [], []
                self._X, self._Y, self._Z  = [], [], []

                # Pause the file reading, returning control to caller
                break

    # --------            

    def close(self):
        self.fid.close()


# ==================================================

if __name__ == "__main__":

    import sys
    from setup import readsup
    setup = readsup('ladim.sup')
    #print sys.argv
    if len(sys.argv) > 1:
        particle_release_file = sys.argv[1]
    else:
        particle_release_file = 'particles.in'
    p = ParticleReleaser(particle_release_file, dt=3600)

    while 1:
        
        #print "==> ", p.release_step, p.particle_counter
        p.read_particles()
        #print p.X
        for i in range(len(p.X)):
            #print " == ", i
            print "%8d %8.2f %8.2f %8.2f %6d" % (
                p.pid[i], p.X[i], p.Y[i], p.Z[i], p.start[i])
        if p.release_step < 0: break
        
    p.close()
    
    #print p.X


    
