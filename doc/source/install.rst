.. index:: installation

.. _installation:

Installation
============

If you are lucky LADiM is already installed at your system. This can be tested
by writing :program:`ladim` on the command line. If it is installed you will
get the reply::

  Starting LADiM --- pyladim configuration ---- ERROR - Configuration file
  ladim.yaml not found

If it is not installed, or the system version is old, you can make a private
install under your user.

TODO: Implement version information as ``ladim --version``

Private LADiM installation
--------------------------

If you do not have system-wide permissions you can install LADiM under your own
user.

First make sure that you are using python 3.x, by typing :program:`python`::

  Python 3.5.2 |Anaconda custom (64-bit)| (default, Jul  2 2016, 17:53:06) [GCC
  4.4.7 20120313 (Red Hat 4.4.7-1)] on linux Type "help", "copyright",
  "credits" or "license" for more information.
  >>>

The python version is the first number. If it is 2.7.x or less you are running
legacy python. Try the command :program:`python3`, or on an anaconda system you
can change to version 3 by ``source activate python3`` or similar.

LADiM is hosted on `github <https://github.com/bjornaa/ladim>`_, download by
the command::

  git clone https://github.com/bjornaa/ladim.git

if you don't have :program:`git` installed download the zip-file from the LADiM
site above.

This makes a :file:`ladim` directory under the present directory.

Now install LADiM locally, user = your login name::

  cd ladim python3 setup.py install --prefix=/home/user

Make sure :file:`/home/user/bin` is in your :envvar:`PATH`. If you want to
override a system LADiM it has to go before python's own bin directory (check:
`which python[3]`). Also add :file:`/home/user/lib/python3.x/site-packages` to
the environment variable :envvar:`PYTHONPATH`, where `x` is the minor python
version.

And you are ready to try out LADiM.
