#!/bin/bash

# Variables: These should be changed/updated for each module

#### Variables Start ####

# Module path, where .sif and meta.yaml will be created
modulepath="../../modules/R-SAIGE"
# List of commands to add to export. Example: exports=("R" "python")
exports=("R")
# Module Description
description="This module exports the R command and includes the SAIGE package for R."
# Optional: list of packages (can be left empty or populated manually)
packages=("SAIGE")

#### Variables End ####

# Create module path (and overwrite existing .sif if it exists)
mkdir -p "$modulepath"
rm -f "$modulepath/singularity.sif"

# Build the Singularity image
singularity build --fakeroot "$modulepath/singularity.sif" singularity.def

# Generate meta.yaml
meta_file="$modulepath/meta.yaml"
{
    echo "description: \"$description\""
    echo "packages:"
    for pkg in "${packages[@]}"; do
        echo "  - $pkg"
    done
    echo "executables:"
    for exe in "${exports[@]}"; do
        echo "  - $exe"
    done
} > "$meta_file"

echo "Module created at $modulepath with meta.yaml."

