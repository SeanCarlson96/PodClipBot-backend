import requests
import subprocess

def is_package_on_pypi(package_name):
    response = requests.get(f'https://pypi.org/pypi/{package_name}/json')
    return response.status_code == 200

# get list of packages in conda environment
result = subprocess.run(['conda', 'list', '-e'], stdout=subprocess.PIPE, text=True)
packages = result.stdout.split('\n')

# remove the '=version' part
packages = [pkg.split('=')[0] for pkg in packages if pkg]

# check each package
for pkg in packages:
    if not is_package_on_pypi(pkg):
        print(f'Package {pkg} is not available on PyPI.')
