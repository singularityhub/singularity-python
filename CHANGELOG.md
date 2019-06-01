# CHANGELOG

This is a manually generated log to track changes to the repository for each release. 
Each section should include general headers such as **Implemented enhancements** 
and **Merged pull requests**. All closed issued and bug fixes should be 
represented by the pull requests that fixed them. This log originated with Singularity 2.4
and changes prior to that are (unfortunately) done retrospectively. Critical items to know are:

 - renamed commands
 - deprecated / removed commands
 - changed defaults
 - backward incompatible changes (recipe file format? image file format?)
 - migration guidance (how to convert images?)
 - changed behaviour (recipe sections work differently)


## [master](https://github.com/singularityware/singularity-python/tree/master)
 - updating Singularity python for version 3 singularity (3.0.0)
 - removed all client functionality in favor of using spython (2.5)
 - build on Google will not extract file counts, etc.

## [v2.4.1](https://github.com/singularityware/singularity-python/releases/tag/v2.4.1) (v2.4.1)

 - changing function to rename image after download to `shutil.move` to allow for cross device downloads.
 - *apps extraction* files limited to those in bin and lib, as the response to the server was too large.
 - **updated tests** to handle secure build
 - to address this [sregisty issue](https://github.com/singularityhub/sregistry/issues/56) the push client does not always state that the upload is finished. In the case that an image is frozen (and 403 status) this message is misleading.


## [v2.4](https://github.com/singularityware/singularity-python/releases/tag/v2.4) (v2.4)

**changed defaults**
 - *sregistry client*: to support use of squashfs images and singularity 2.4, the default upload is not compressed, assuming squashfs, and the default download is not decompressed. To still compress an image add the `--compress` flag on push, and the `--decompress` flag on pull.
