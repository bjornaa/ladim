.. .. author:: Bjørn Ådlandsvik <bjorn@imr.no>

LADIM configuration
===================

The LADiM model system is highly configurable using a separate configuration file. The goal is that a user should not have to touch the code, every
necessary aspect should be customizable by the configuration file.

The name of the configuration file is given as a command line argument to the
main ladim script. If the name is missing, a default name of :file:`ladim.yaml`
is supposed.

It is a goal to provide sane defaults in the configuration file, so that
enhancements of the configuration setup do not break existing configuration
files.

The configuration file format is a subset of :abbr:`yaml
(YAML Ain't Markup Language)` (`<http:yaml.org>`_). Knowledge of yaml is not
necessary. The example configuration files are self-describing and can
easily be modified.

Note that the indentation in a yaml file is mandatory, it i spart of the syntax. The indentation has to be done by spaces, not tabs. Reasonable editors will recognize yaml-files by the extension and will automatically produce spaces when you hit the tab key.

.. seealso::
  Module :mod:`configuration`
    Documentation of the :mod:`configuration` module

An example configuration file
-----------------------------

Below is an example configuration file,
