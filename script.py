import re

# define the source and target file names
source_file_name = 'source.txt'
target_file_name = 'requirements.txt'

# read the content of the source file
with open(source_file_name, 'r') as source_file:
    content = source_file.read()

# find the package names using regex
packages = re.findall(r"'name'\s*:\s*'([^']*)',\s*'version'\s*:", content)

# write the package names to the target file
with open(target_file_name, 'w') as target_file:
    for package in packages:
        target_file.write(package + '\n')

print('Packages were written to', target_file_name)
