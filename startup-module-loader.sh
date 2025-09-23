#!/bin/bash

LOGFILE="/var/log/startup-module-load.log"
R_MODULE="r-tre-all-1"
PY_MODULE="tre-python"
MODULE_DIR="/genesandhealth/lmod/modules"
OVERLAY="/genesandhealth/lmod/modules/jupyter.sqfs"
KERNEL_DIR="/home/ivm/.local/share/jupyter/kernels"
SINGULARITY_BIN="/usr/local/bin/singularity"

echo "Starting $(date)" >> "$LOGFILE"

# Wait until /home/ivm exists, timeout after 120 seconds
TIMEOUT=120
WAITED=0
SLEEP=5

while [ ! -d "/home/ivm" ]; do
    if [ "$WAITED" -ge "$TIMEOUT" ]; then
        echo "Timeout waiting for /home/ivm directory" >> "$LOGFILE"
        exit 1
    fi
    echo "/home/ivm not found, sleeping..." >> "$LOGFILE"
    sleep $SLEEP
    WAITED=$((WAITED + SLEEP))
done

echo "/home/ivm found, proceeding..." >> "$LOGFILE"

# Wait until /home/ivm exists, timeout after 120 seconds
while [ ! -d "$MODULE_DIR" ]; do
    if [ "$WAITED" -ge "$TIMEOUT" ]; then
        echo "Timeout waiting for $MODULE_DIR directory" >> "$LOGFILE"
        exit 1
    fi
    echo "$MODULE_DIR not found, sleeping..." >> "$LOGFILE"
    sleep $SLEEP
    WAITED=$((WAITED + SLEEP))
done

echo "$MODULE_DIR found, proceeding..." >> "$LOGFILE"

# Load the default R  module
RETRIES=10
MODULE_LOADED=false

for i in $(seq 1 $RETRIES); do
    echo "Attempt $i to load $R_MODULE" >> "$LOGFILE"
    sudo -u ivm /usr/local/bin/module-manager load "$R_MODULE" >> "$LOGFILE" 2>&1
    if [[ $? -eq 0 ]]; then
        echo "Module $R_MODULE loaded successfully." >> "$LOGFILE"
        MODULE_LOADED=true
        break
    fi
    sleep $SLEEP
done

if [ "$MODULE_LOADED" = false ]; then
    echo "$(date): Module load failed after $RETRIES attempts" >> "$LOGFILE"
fi

# Load the default python  module
RETRIES=10
MODULE_LOADED=false

for i in $(seq 1 $RETRIES); do
    echo "Attempt $i to load $PY_MODULE" >> "$LOGFILE"
    sudo -u ivm /usr/local/bin/module-manager load "$PY_MODULE" >> "$LOGFILE" 2>&1
    if [[ $? -eq 0 ]]; then
        echo "Module $PY_MODULE loaded successfully." >> "$LOGFILE"
        MODULE_LOADED=true
        break
    fi
    sleep $SLEEP
done

if [ "$MODULE_LOADED" = false ]; then
    echo "$(date): Module load failed after $RETRIES attempts" >> "$LOGFILE"
fi

# Kernel creation for all modules
echo "[$(date)] Starting kernel creation..." >> "$LOGFILE"

# Ensure kernel directory exists (as ivm)
sudo -u ivm mkdir -p "$KERNEL_DIR"

echo "Listing modules in $MODULE_DIR:" >> "$LOGFILE"
MODULE_PATHS=$(sudo -u ivm find "$MODULE_DIR" -mindepth 1 -maxdepth 1 -type d)
echo $MODULE_PATHS >> "$LOGFILE"

# Loop through each module directory
for module_path in $MODULE_PATHS; do
    echo " -> [DEBUG] module_path: $module_path" >> "$LOGFILE"

    module_name=$(basename "$module_path")
    sif_path="$module_path/singularity.sif"

    echo "[$(date)] Processing module: $module_name" >> "$LOGFILE"

    if ! sudo -u ivm test -f "$sif_path"; then
    echo " -> [WARN] singularity.sif missing or inaccessible in $module_name, skipping." >> "$LOGFILE"
    continue
    fi

    # Detect R version
    R_VER_OUTPUT=$(sudo -u ivm "$SINGULARITY_BIN" exec "$sif_path" R --version 2>/dev/null)
    if [[ $? -eq 0 ]]; then
        if [[ "$R_VER_OUTPUT" =~ R\ version\ ([0-9]+\.[0-9]+) ]]; then
            SHORT_R_VER="${BASH_REMATCH[1]}"
            echo " -> [OK] Found R version $SHORT_R_VER" >> "$LOGFILE"

            kernel_name="${module_name}-r"
            kernel_path="${KERNEL_DIR}/${kernel_name}"
            sudo -u ivm mkdir -p "$kernel_path"

            sudo -u ivm cat <<EOF | tee "${kernel_path}/kernel.json" > /dev/null
{
  "argv": [
    "$SINGULARITY_BIN",
    "exec",
    "--bind",
    "/genesandhealth/",
    "--overlay",
    "$OVERLAY",
    "$sif_path",
    "/opt/view/bin/R",
    "--slave",
    "-e",
    "IRkernel::main()",
    "--args",
    "{connection_file}"
  ],
  "env": {
    "SINGULARITYENV_R_LIBS": "\$R_LIBS:/opt/R/$SHORT_R_VER/"
  },
  "display_name": "$module_name (R)",
  "language": "R"
}
EOF
        else
            echo " -> [WARN] Could not extract R version string" >> "$LOGFILE"
        fi
    else
        echo " -> [INFO] R not found in $module_name container" >> "$LOGFILE"
    fi

    # Detect Python version
    PY_VER_OUTPUT=$(sudo -u ivm "$SINGULARITY_BIN" exec "$sif_path" python3 --version 2>/dev/null)
    if [[ $? -eq 0 ]]; then
        if [[ "$PY_VER_OUTPUT" =~ Python\ ([0-9]+\.[0-9]+) ]]; then
            SHORT_PY_VER="${BASH_REMATCH[1]}"
            echo " -> [OK] Found Python version $SHORT_PY_VER" >> "$LOGFILE"

            kernel_name="${module_name}-py"
            kernel_path="${KERNEL_DIR}/${kernel_name}"
            bash_kernel_path="${KERNEL_DIR}/${module_name}-bash"
            sudo -u ivm mkdir -p "$kernel_path"
            sudo -u ivm mkdir -p "$bash_kernel_path"

            cat <<EOF | sudo -u ivm tee "${kernel_path}/kernel.json" > /dev/null
{
  "argv": [
    "$SINGULARITY_BIN",
    "exec",
    "--bind",
    "/genesandhealth/",
    "--overlay",
    "$OVERLAY",
    "$sif_path",
    "/opt/view/bin/python$SHORT_PY_VER",
    "/opt/python/$SHORT_PY_VER/ipykernel_launcher.py",
    "-f",
    "{connection_file}"
  ],
  "env": {
    "SINGULARITYENV_PYTHONPATH": "/opt/python/$SHORT_PY_VER/"
  },
  "display_name": "$module_name (python)",
  "language": "python"
}
EOF
            cat <<EOF | sudo -u ivm tee "${bash_kernel_path}/kernel.json" > /dev/null
{
  "argv": [
    "$SINGULARITY_BIN",
    "exec",
    "--bind",
    "/genesandhealth/",
    "--overlay",
    "$OVERLAY",
    "$sif_path",
    "/opt/view/bin/python$SHORT_PY_VER",
    "-m",
    "bash_kernel",
    "-f",
    "{connection_file}"
  ],
  "env": {
    "SINGULARITYENV_PYTHONPATH": "/opt/python/$SHORT_PY_VER/"
  },
  "display_name": "$module_name (bash)",
  "language": "bash"
}
EOF
        else
            echo " -> [WARN] Could not extract Python version string" >> "$LOGFILE"
        fi
    else
        echo " -> [INFO] Python3 not found in $module_name container" >> "$LOGFILE"
    fi

done

echo "[$(date)] Kernel creation completed." >> "$LOGFILE"
