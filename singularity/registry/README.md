# Singularity Registry

This is the base for functions and clients in python to work with a Singularity Registry. Specifically:

 - [main](main): contains functions for the `sregistry` command line tool. This is an executable installed to your machine when the `singularity` module is installed, and what you use when you want to run a command from a terminal prompt.
 - [client](client): contains functions to instantiate a client (class) that handles authentication and making calls. For example, the command line tool above `sregistry` internally instantiates the client to do most calls.
 - [utils](utils): contains various utility functions for a Singularity registry.
 - [auth.py](auth.py): authentication functions used by all of the above.
