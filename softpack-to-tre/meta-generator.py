import yaml
import re
import sys

# Get yaml from input.
original_yaml = sys.stdin.read()
yaml_data = yaml.safe_load(original_yaml)

# Get description.
desc_and_executables = yaml_data.get("description", "")
desc = desc_and_executables.strip().splitlines()[0]

# Get all executables.
exec_pattern = r"- (.+)"
executables = re.findall(exec_pattern, desc_and_executables)

# Get all packages.
cleaned_packages = []
for pkg in yaml_data.get("packages", []):
    pkg_name = pkg.split("@")[0]
    cleaned_packages.append(pkg_name)

# Make new yaml data in the correct format.
new_data = {
    "description": desc,
    "packages": cleaned_packages,
    "executables": executables
}

# Save new yaml to a file.
new_yaml = yaml.dump(new_data, sort_keys=False)
output_filename = "meta.yaml"

with open(output_filename, "w") as f:
    f.write(new_yaml)
