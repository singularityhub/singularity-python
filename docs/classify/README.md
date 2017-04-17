

# Classify your container

Singularity python provides functions for quickly assessing the base operating system of your container, retrieving a list of software tags that are relevant when this base is subtracted, and getting similarity scores of your container to a library of base software. These metrics are based on file paths, and not content hashes. If you are looking for more robust similarity metrics, see <a href="/singularity-python/reproducibility">reproducibility metrics</a>


## Estimate the OS

You can do this on the command line as follows:

```bash
$ shub --os --image docker://ubuntu:latest
Most similar OS found to be  ubuntu:16.04
ubuntu:16.04
```

or to do this from within Python, see [classify_image/estimate_os.py](classify_image/estimate_os.py).


## Get software tags
Singularity Hub uses a simple algorithm to obtain a likely list of software that is important to your image. It assumes that (most) core installed software is in a folder called `bin`, and returns the list of these files with the estimated base image subtracted. You can do this as follows:

```
shub --image docker://python:latest --tags
['2to3-2.7', '2to3-3.6', 'a2p', 'aclocal-1.14', 'addr2line', 'ar', 'as', 'autoconf', 'autoheader', 'autom4te', 'automake-1.14', 'autoreconf', 'autoscan', 'autoupdate', 'bzcat', 'bzdiff', 'bzexe', 'bzgrep', 'bzip2recover', 'bzmore', 'bzr', 'c++filt', 'c89-gcc', 'c99-gcc', 'c_rehash', 'compile_et', 'config_data', 'corelist', 'cpan', 'cpp-4.9', 'curl', 'curl-config', 'dh_autotools-dev_restoreconfig', 'dh_autotools-dev_updateconfig', 'dh_python2', 'dwp', 'easy_install-3.6', 'elfedit', 'enc2xs', 'fc-cache', 'fc-cat', 'fc-list', 'fc-match', 'fc-pattern', 'fc-query', 'fc-scan', 'fc-validate', 'file', 'find2perl', 'freetype-config', 'g++-4.9', 'gapplication', 'gcc-4.9', 'gcc-ar-4.9', 'gcc-nm-4.9', 'gcc-ranlib-4.9', 'gcov-4.9', 'gdbus', 'gdbus-codegen', 'gdk-pixbuf-csource', 'gdk-pixbuf-pixdata', 'gencat', 'geoiplookup', 'geoiplookup6', 'git', 'git-shell', 'git-upload-pack', 'glib-genmarshal', 'glib-gettextize', 'glib-mkenums', 'gobject-query', 'gprof', 'gresource', 'gsettings', 'gtester', 'gtester-report', 'h2ph', 'h2xs', 'hg', 'hg-ssh', 'idle3.6', 'ifnames', 'instmodsh', 'json_pp', 'krb5-config.mit', 'lcf', 'ld.bfd', 'ld.gold', 'libnetcfg', 'libpng12-config', 'libtoolize', 'libwmf-config', 'lzmainfo', 'm4', 'make', 'make-first-existing-target', 'mtrace', 'mysql_config', 'nm', 'objcopy', 'objdump', 'openssl', 'patch', 'pcre-config', 'perlbug', 'perldoc', 'perlivp', 'pg_config', 'piconv', 'pip', 'pip3', 'pip3.6', 'pl2pm', 'pod2html', 'pod2man', 'pod2text', 'pod2usage', 'podchecker', 'podselect', 'prename', 'prove', 'psed', 'pstruct', 'ptar', 'ptardiff', 'ptargrep', 'pyclean', 'pycompile', 'pydoc2.7', 'pydoc3.6', 'pygettext2.7', 'python2.7', 'python3.6m', 'python3.6m-config', 'pyvenv-3.6', 'ranlib', 'readelf', 'rpcgen', 'run-mailcap', 'scp', 'sftp', 'shasum', 'size', 'sotruss', 'splain', 'sprof', 'ssh', 'ssh-add', 'ssh-agent', 'ssh-argv0', 'ssh-copy-id', 'ssh-keygen', 'ssh-keyscan', 'strings', 'strip', 'svn', 'svnadmin', 'svnauthz', 'svnauthz-validate', 'svndumpfilter', 'svnlook', 'svnmucc', 'svnrdump', 'svnserve', 'svnsync', 'svnversion', 'tclsh8.6', 'ucf', 'ucfq', 'ucfr', 'update-mime-database', 'update-mime-database.real', 'wget', 'wish8.6', 'x86_64-pc-linux-gnu-pkg-config', 'xml2-config', 'xslt-config', 'xsubpp', 'xz', 'xzdiff', 'xzgrep', 'xzless', 'xzmore', 'zipdetails']
```


We also provide an example within python at [classify_image/derive_tags.py](classify_image/derive_tags.py). If you do this programatically, you can change the folder(s) that are included, meaning that you could get a custom list of software (eg, libraries in `lib`, or python packages in `site-packages`).


## Compare to base OS
If you want to get a complete list of scores for your image against a core set of latest [docker-os](singularity/analysis/packages/docker-os) images:

```
shub --image docker://python:latest --oscalc
```

or again see [this example](classify_image/estimate_os.py) for doing this from within python.

You can also generate a [dynamic plot](https://singularityware.github.io/singularity-python/docs/classify/classify_image/) for this data:

```
shub --image docker://python:latest --osplot
```
