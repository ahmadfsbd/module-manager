#!/bin/bash

# === Input ===
SIF="$1"

if [[ -z "$SIF" || ! -f "$SIF" ]]; then
  echo "Usage: $0 /full/path/to/singularity.sif"

  exit 1
fi

SIF_PATH=$(realpath "$SIF")

# Extract type (users/groups), group/user, module and version.
TYPE=$(echo "$SIF_PATH" | grep -oP 'installs/\K[^/]+' )
OWNER=$(echo "$SIF_PATH" | grep -oP "${TYPE}/\K[^/]+" )
MODULE=$(echo "$SIF_PATH" | grep -oP "${OWNER}/\K[^/]+" )
VERSION_DIR=$(echo "$SIF_PATH" | grep -oP "${MODULE}/\K[^/]+" )
VERSION=$(echo "$VERSION_DIR" | cut -d'-' -f1)

MODULE_FULL="${MODULE}-${VERSION}"

# Compose URL with information from the path.
URL="https://gitlab.internal.sanger.ac.uk/hgi-projects/softpack/artifacts/-/raw/main/environments/${TYPE}/${OWNER}/${MODULE_FULL}/softpack.yml"

OUTFILE="meta.yaml"

# Generate meta.yaml file for the given module.
curl -s "$URL" | python3 meta-generator.py "$OUTFILE"

echo "✅ Done. Successfully written to $OUTFILE"

# Upload the singularity.sif and meta.yaml file to google cloud.
GCLOUD_PATH="gs://qmul-testing-library-red/modules/${MODULE_FULL}/"

gcloud storage cp "$SIF" "$GCLOUD_PATH"
gcloud storage cp "$OUTFILE" "$GCLOUD_PATH"

echo "✅ Done. Successfully copied singularity and meta files to gcloud."
