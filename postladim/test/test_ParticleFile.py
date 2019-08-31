import os
import pytest

import numpy as np
# import xarray as xr
# from pathlib import Path
from netCDF4 import Dataset
from postladim import ParticleFile


@pytest.fixture(scope="module")
def particle_file():
    # set up
    # Return a small particle file
    pfile = "test.nc"
    nparticles = 3
    X = np.array(
        [[0, np.nan, np.nan], [1, 11, np.nan], [2, np.nan, 22], [np.nan, np.nan, 23]]
    )
    Y = np.array(
        [[2, np.nan, np.nan], [3, 8, np.nan], [4, np.nan, 9], [np.nan, np.nan, 10]]
    )
    ntimes = X.shape[0]
    pid = np.multiply.outer(ntimes * [1], list(range(nparticles)))
    pid[np.isnan(X)] = -99  # Undefined integer
    time = 3600 * np.arange(ntimes)  # hourly timesteps
    count = (np.ones(np.shape(X)) - np.isnan(X)).sum(axis=1)
    with Dataset(pfile, mode="w") as nc:
        # Dimensions
        nc.createDimension("particle", nparticles)
        nc.createDimension("particle_instance", None)
        nc.createDimension("time", ntimes)
        # Variables
        v = nc.createVariable("time", "f8", ("time",))
        v.units = "seconds since 1970-01-01 00:00:00"
        v = nc.createVariable("particle_count", "i", ("time",))
        v = nc.createVariable("start_time", "f8", ("particle",))
        v.units = "seconds since 1970-01-01 00:00:00"
        v = nc.createVariable("position", "i", ("particle",))
        v = nc.createVariable("pid", "i", ("particle_instance",))
        v = nc.createVariable("X", "f4", ("particle_instance"))
        v = nc.createVariable("Y", "f4", ("particle_instance"))
        # Data
        nc.variables["time"][:] = time
        nc.variables["particle_count"][:] = count
        nc.variables["start_time"][:] = time[:nparticles]
        nc.variables["position"][:] = 11111 * np.arange(nparticles)
        nc.variables["pid"][:] = [v for v in pid.flat if v >= 0]
        nc.variables["X"][:] = [v for v in X.flat if not np.isnan(v)]
        nc.variables["Y"][:] = [v for v in Y.flat if not np.isnan(v)]

    yield pfile

    # tear down
    os.remove(pfile)




# def test_open():
#    with pytest.raises(FileNotFoundError):
#        pf = ParticleFile("no_such_file.nc")





def test_count(particle_file):
    """Alignment of time frames in the particle file."""
    with ParticleFile(particle_file) as pf:
        assert pf.num_times == 4
        assert all(pf.start == [0, 1, 3, 5])
        assert list(pf.count) == [1, 2, 2, 1]
        assert list(pf.end) == [1, 3, 5, 6]
        assert len(pf) == 4
        assert pf.num_particles == 3


def test_time(particle_file):
    """Time handled correctly"""
    with ParticleFile(particle_file) as pf:
        assert pf.time[3] == np.datetime64("1970-01-01 03")
        times2 = [np.datetime64(t) for t in ["1970-01-01", "1970-01-01 01"]]
        assert all(pf.time[:2] == times2)
        # Old callable notation still works
        assert pf.time(3) == pf.time[3]
        assert str(pf.time(3)) == "1970-01-01T03:00:00"


def test_variables(particle_file):
    """Indentifies the variables to correct category"""
    with ParticleFile(particle_file) as pf:
        assert pf.instance_variables == ["pid", "X", "Y"]
        assert pf.particle_variables == ["start_time", "position"]


def test_pid(particle_file):
    """The pid is correct"""
    with ParticleFile(particle_file) as pf:
        assert pf.pid.isel(time=0) == 0
        assert pf["pid"][0] == 0
        assert pf.pid[0] == 0
        assert all(pf.pid[1] == [0, 1])
        assert list(pf.pid[2]) == [0, 2]
        assert pf.pid[3] == 2


# --- InstanceVariable tests ---

# Detemine how this should work
def test_pid2(particle_file):
    """The pid from a Instance variable"""
    with ParticleFile(particle_file) as pf:
        X = pf.X
        # assert X.pid.isel(time=0) == 0
        # assert pf["pid"][0] == 0
        # assert pf.pid[0] == 0
        # assert all(pf.pid[1] == [0, 1])
        # assert list(pf.pid[2]) == [0, 1]
        # assert pf.pid[3] == 1


def test_getX(particle_file):
    with ParticleFile(particle_file) as pf:
        assert pf["X"].isel(time=0) == 0
        assert pf["X"][0] == 0
        assert pf.X[0] == 0
        assert all(pf.X[1] == [1, 11])
        assert all(pf.X[2] == [2, 22])
        assert pf.X[3] == 23


def test_X_slice(particle_file):
    """Can read variables with time slices"""
    with ParticleFile(particle_file) as pf:
        X = pf.X
        V = pf.X[1:3]
        assert len(V) == 2
        assert all(V[0] == X[1])
        assert all(V[1] == X[2])
        assert all(V.da == [1, 11, 2, 22])
        assert all(V.count == [2, 2])
        assert all(V.time == X.time[1:3])
        assert all(V.pid == [0, 1, 0, 2])
        V = X[:]
        for n in range(len(X)):
            assert all(V[n] == X[n])
        with pytest.raises(IndexError):
            pf.X[::2]  # Do not accept strides != 1


def test_select_pid(particle_file):
    with ParticleFile(particle_file) as pf:
        X = pf.X
        assert all(X._sel_pid_value(0) == [0, 1, 2])
        assert all(X.sel(pid=2) == [22, 23])


def test_full(particle_file):
    with ParticleFile(particle_file) as pf:
        X = pf.X
        V = X.full()
        assert V[0, 0] == 0
        assert np.isnan(V[0, 1])
        assert np.isnan(V[0, 2])
        assert V[1, 0] == 1
        assert V[1, 1] == 11
        assert np.isnan(V[1, 2])
        assert V[2, 0] == 2
        assert np.isnan(V[2, 1])
        assert V[2, 2] == 22
        assert np.isnan(V[3, 0])
        assert np.isnan(V[3, 1])
        assert V[3, 2] == 23



def rest_slice_advanced(particle_file):
    """More advanced slicing"""
    with ParticleFile(particle_file) as pf:
        I = [True, True, False, True, False, False]
        assert list(pf.X[I] == [5, 6, 7])
        assert list(pf.X[[0, 1, 3]] == [5, 6, 7])
        # Accept only integer or boolean sequences
        with pytest.raises(IndexError):
            pf.X["abc"]  # Not a sequence of integers
        with pytest.raises(IndexError):
            pf.X[3.14]  # Not integer, slice, or sequence
        with pytest.raises(IndexError):  # Not a sequence
            pf.X[{"a": 1}]  # Not integer, slice, or sequence
        # Strange feature, inherited from NetCDF4
        assert pf.X[[3.14]] == pf.X[[3]]


def test_position(particle_file):
    with ParticleFile(particle_file) as pf:
        pos = pf.position(1)
        assert all(pos.X == pf.X[1])
        assert all(pos.Y == pf.Y[1])
        X, Y = pf.position(2)
        assert all(X == pf.X[2])
        assert all(Y == pf.Y[2])


def test_trajectory(particle_file):
    with ParticleFile(particle_file) as pf:
        X, Y = pf.trajectory(2)
        assert all(X == [22, 23])
        assert all(Y == [9, 10])
        traj = pf.trajectory(0)
        assert len(traj) == 3
        assert all(traj.time == pf.time[:-1])
        assert all(traj.X == pf.X.sel(pid=0))
        assert all(traj.Y == pf.Y.sel(pid=0))
