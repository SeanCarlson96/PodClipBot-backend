import pkg_resources
import subprocess

# Get the list of installed distributions
dists = [d for d in pkg_resources.working_set]

with open('requirements.txt', 'w') as f:
    for d in dists:
        req = f"{d.project_name}=={d.version}"
        # Write the package and version to the file
        f.write(f"{req}\n")
