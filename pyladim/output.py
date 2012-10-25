# -*- coding: utf-8 -*-

import datetime
from netCDF4 import Dataset

# For each possible variable, provide a
# netcdf type and a dictionary of netcdf attributes 
# Example:
#  ('f4', dict(standard_name='longitude', units='degrees_east'))

# NetCDF data types for the variables
variables_nctype = dict(
    pid = 'i4',
    X   = 'f4',
    Y   = 'f4',
    Z   = 'f4',
    lon = 'f4',
    lat = 'f4'
)

# NetCDF attributes
variables_ncatt = dict(
    pid = dict(long_name     = 'particle identifier',
               cf_role       = 'trajectory_id'),
    X   = dict(long_name     = 'grid X-coordinate of particles'),
    Y   = dict(long_name     = 'grid Y-coordinate of particles'),
    Z   = dict(long_name     = 'particle depth',
               standard_name = 'depth',
               units         = 'm',
               positive      = 'down'),
    lon = dict(long_name     = 'particle longitude',
               standard_name = 'longitude',
               units         = 'degrees_east'),
    lat = dict(long_name     = 'particle latitude',
               standard_name = 'latitude',
               units         = 'degrees_north'),
    
    )
    



class OutPut(object):

    def __init__(self, setup):

        nc = Dataset(setup.output_filename, mode='w', 
                     format="NETCDF3_CLASSIC")

        # Dimensions
        nc.createDimension('particle_index', None)  # unlimited
        nc.createDimension('time', setup.Nout)

        # Coordinate variable for time
        v = nc.createVariable('time', 'f8', ('time',))
        v.long_name = 'time'
        v.standard_name = 'time'
        v.units = 'seconds since %s' % setup.start_time
        #v.calendar = 'proleptic_gregorian'
        # Ha mer fleksibilitet av valg av referansetid

        v = nc.createVariable('pstart', 'i4', ('time',))
        v.long_name = 'start index for particle distribution'
        v = nc.createVariable('pcount', 'i4', ('time',))
        v.long_name = 'number of particles'

        # Oputput variables
        for var in setup.output_variables:
            v = nc.createVariable(var, variables_nctype[var],
                                  ('particle_index',))
            atts = variables_ncatt[var]
            for att in atts:
                setattr(v, att, atts[att])

        # Global attributes
        nc.Conventions = "CF-1.5"
        nc.institution = "Institute of Marine Research"
        nc.source = "Lagrangian Advection and DIffusion Model, python version"
        nc.history = "%s created by pyladim" % datetime.date.today()
        
        self.nc = nc
        #self.Nout = Nout
        self.outcount = 0
        self.pstart   = 0
        self.outstep  =  setup.output_period * setup.dt
        self.output_variables = setup.output_variables
        self.pvars = setup.output_variables
        
    # --------------
 
    def write(self, state):
        """
        Write a particle distribution
        """

        Npar = len(state) 
        t = self.outcount
        nc = self.nc

        # Write to time variables
        nc.variables['pstart'][t] = self.pstart
        nc.variables['pcount'][t] = Npar     
        nc.variables['time'][t] = t * self.outstep

        # Write to particle properties
        T = slice(self.pstart, self.pstart + Npar)
        for var in self.output_variables:
            nc.variables[var][T] = getattr(state, var)

        # Write 
        self.pstart += Npar
        self.outcount += 1

    # --------------

    def close(self):

        self.nc.close()




    
