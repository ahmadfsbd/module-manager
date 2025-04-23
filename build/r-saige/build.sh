#!/bin/bash

# Module path, where .sif and exports will be created
modulepath="../../modules/R-SAIGE"

# List of commands to add to exports (each on a new line)
# Example: exports=("R" "python")
exports=("R")

# Create module path (and overwrite existing .sif if it exists)
mkdir -p "$modulepath"
rm -f "$modulepath/singularity.sif"

# Build the Singularity image
singularity build --fakeroot "$modulepath/singularity.sif" singularity.def

# Path to the exports file
exports_file="$modulepath/exports"

# Overwrite the exports file with the new entries
: > "$exports_file"
for cmd in "${exports[@]}"; do
	  echo "$cmd" >> "$exports_file"
  done

