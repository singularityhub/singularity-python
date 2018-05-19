# Singularity Python

[![Build Status](https://travis-ci.org/singularityware/singularity-python.svg?branch=master)](https://travis-ci.org/singularityware/singularity-python)

Singularity Python is a python module and command line tool to provide helpers for working with <a href="https://singularityware.github.io" target="_blank">Singularity</a> containers, specifically providing functions to visualize, package, and compare containers. 

 - If you are looking for the Singularity Python client to pull, build, and otherwise wrap Singularity functions, then please see the repository [singularity-cli](https://singularityhub.github.io/singularity-cli) for the [spython](https://pypi.org/project/spython/) module.
 - If you are looking for local management and interaction with various storage locations (e.g., to pull and inspect containers in Singularity Hub, Registry, or other cloud resource) then please see the [Global Client](https://singularityhub.github.io/sregistry-cli) for the `sregistry` module.

## Install
You have the option to install only the dependencies that are needed for your functionality of interest.

```bash
# All
pip install singularity

# Metrics and analysis dependencies
pip install singularity[metrics]

# Building on Google Cloud
pip install singularity[google[
```


We currently require Python > version 3 to use various timezone functions. If you are unable to install version 3.0, we provide a [Singularity.container](Singularity.container) for you to use instead. This is the recommended approach as some older versions of Python do not support generation of the timestamp. See the [installation docs](https://github.com/singularityware/singularity-python/wiki/Installation) for your different options.

## License

This code is licensed under the Affero GPL, version 3.0 or later [LICENSE](LICENSE).
Please see our [complete docs](https://github.com/singularityware/singularity-python/wiki)

## Help and Contribution
Please contribute to the package, or post feedback and questions as <a href="https://github.com/singularityware/singularity-python" target="_blank">issues</a>. For points that require discussion of the larger group, please use the <a href="https://groups.google.com/a/lbl.gov/forum/#!forum/singularity" target="_blank">Singularity List</a>
