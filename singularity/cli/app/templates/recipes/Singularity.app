Bootstrap: {{ bootstrap }}
From: {{ from }}

%environment

%labels

%help

%files

%post

%runscript

##############################
# {{ app }}
##############################

%apprun {{ app }}

%applabels {{ app }}

%appinstall {{ app }}

%appenv {{ app }}

%apphelp {{ app }}

%appfiles {{ app }}
