import numpy as np
from ladim.ibms import light


class IBM:

    def __init__(self, config):

        # Constants
        mortality = 0.17    # [days-1]

        # mm2m = 0.001
        # g = 9.81
        # tempB = 7.0  # setter default temperatur

        self.k = 0.2             # Light extinction coefficient
        self.swim_vel = 5E-4     # m/s
        self.D = 1E-3            # Vertical mixing [m*2/s]

        self.dt = config.dt
        self.mortality_factor = np.exp(-mortality*self.dt/86400)

    def update_ibm(self, grid, state, forcing):

        # Mortality
        state.super *= self.mortality_factor

        # Age in degree-days
        temp = forcing.sample_field(state.X, state.Y, state.Z, 'temp')
        state.age += temp * state.dt / 86400

        # Light at depth
        _, lat = grid.lonlat(state.X, state.Y)  # ignore longitude
        light0 = light.surface_light(forcing.time, lat)
        Eb = light0 * np.exp(-self.k*state.Z)

        # Swimming velocity
        W = np.zeros_like(state.X)
        # Upwards if light enough
        W[Eb >= 0.01] = self.swim_vel
        # Downwards if salinity < 20
        salt = forcing.sample_field(state.X, state.Y, state.Z, 'salt')
        W[salt < 20] = -self.swim_vel

        # Random diffusion velocity
        if self.vertical_diffusion:
            rand = np.random.normal(size=len(W))
            W += rand * (2*self.D/self.dt)**0.5

        # Update vertical position
        state.Z += W * self.dt
