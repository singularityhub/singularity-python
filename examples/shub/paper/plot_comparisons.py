#!/usr/bin/env python3

import numpy
import os
import pickle
import seaborn as sns
import matplotlib.pyplot as plt


container_names = ['vsoch/singularity-hello-world',
                   'researchapps/quantum_state_diffusion',
                   'vsoch/pe-predictive']

storage = "/home/vanessa/Documents/Work/singularity/hub"
results = pickle.load(open('%s/results.pkl' %storage,'rb'))
df = results['df']

metrics = ['size','build_time_seconds']

# Set up the matplotlib figure
sns.set(style="white", palette="muted", color_codes=True)

for metric in metrics:
    for c in range(len(container_names)):
        container_name = container_names[c]  
        values = df[metric][df.name == container_name].tolist()
        sns.distplot(values, kde=False, rug=True)

        x=axes_lookup[c][0]
        y=axes_lookup[c][0]
        sns.distplot(values, color="m", ax=axes[x,y])

plt.setp(axes, yticks=[])
plt.tight_layout()



