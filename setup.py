# -*- coding: utf-8 -*-

import datetime
import ConfigParser

# Make setup a class ?, with this as methods
# 


def readsup(supfile):

    # Default values for optional setup elements
    defaults = dict(
        dt = '3600',        # one hour
        stop_time = "",   # compute from nsteps
        nsteps    = "",   # compute from stop_time
        output_period         = "", 
        output_period_seconds = "",
        output_period_hours   = "",
        )

    config = ConfigParser.ConfigParser(defaults)

    config.read(supfile)

    setup = {}

    # ---------------
    # Section [time]
    # ---------------

    # Mangler: sjekk: både stop_time og nsteps finnes
    #           gi warning dersom ikke stemmer overens
    # Dersom total_time ikke delelig med dt
    #    Reduser stop_time tilsvarende.
    #   => tidsteg 1 dag, gjør ikke noe for total_time = 3 hours
    #    Ta med å gi warning

    setup['dt'] = int(config.get('time', 'dt'))

    start_time = config.get('time', 'start_time')
    setup['start_time'] = datetime.datetime.strptime(start_time, 
                                   "%Y-%m-%d %H:%M:%S")

    stop_time = config.get('time', 'stop_time')
    nsteps = config.get('time', 'nsteps')

    if not stop_time in ["", "None", None]:
        setup['stop_time'] = datetime.datetime.strptime(stop_time, 
                                   "%Y-%m-%d %H:%M:%S")
        total_time = setup['stop_time'] - setup['start_time']
        setup['nsteps'] = ( (total_time.days*86400 + total_time.seconds) 
                             // setup['dt'] )
    elif not nsteps in ["", "None", None]:
        setup['nsteps'] = int(nsteps)
        setup['stop_time'] = setup['start_time']    \
            + datetime.timedelta(seconds=setup['dt']*setup['nsteps'])
    else:
        # Raise exception instead
        print "***Error in setup: must have nsteps or stop_time"
        import sys; sys.exit(1)

    # ----------
    # Output
    # ----------

    # Lage seksjon [output] i sup-fil ??
        
    setup['output_filename'] = config.get('time', 'output_filename')

    outper   = config.get('time', 'output_period')
    outper_s = config.get('time', 'output_period_seconds')
    outper_h = config.get('time', 'output_period_hours')

    if not outper in ["", None, "None"]:
        outper = int(outper)
    elif not outper_s in ["", None, "None"]:
        outper = int(outper_s) // setup['dt']
    elif not outper_h in ["", None, "None"]:
        outper = int(outper_h) * 3600 // setup['dt']
    setup['output_period'] = outper

    # Number of time frames in output, add one for initial distribution
    setup['Nout'] = 1 + setup['nsteps'] // outper
        
    return setup

# --------------

def writesup(setup):
    # Make an explicit sequence of keys
    # Can be improved with ordered_dict (from python 2.7)
    time_keys = ['start_time', 'stop_time', 'dt', 'nsteps']
    output_keys = ['output_filename', 'output_period', 'Nout']
    
    for key in time_keys:
        print "%20s :" % key, setup[key]

    print 40*"-"

    for key in output_keys:
        print "%20s :" % key, setup[key]



# ---
# Ha en write-sup method ??
# Får penere utskrift når kjører test


# -------------
# Simple test
# -------------

if __name__ == '__main__':
    supfile = 'ladim.sup'
    setup = readsup(supfile)
    writesup(setup)

                 

