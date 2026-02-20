#!/usr/bin/env bash
set -euo pipefail

# Configure DVC remote for DagsHub without hardcoding credentials.
# Required env vars:
#   DAGSHUB_USER
#   DAGSHUB_TOKEN
# Optional env vars:
#   DAGSHUB_BASE_URL (default: https://dagshub.com)
#   DAGSHUB_REPO_OWNER (default: Brunobs13)
#   DAGSHUB_REPO_NAME (default: networksecurity)
#   DVC_REMOTE_NAME (default: origin)

DAGSHUB_BASE_URL="${DAGSHUB_BASE_URL:-https://dagshub.com}"
DAGSHUB_REPO_OWNER="${DAGSHUB_REPO_OWNER:-Brunobs13}"
DAGSHUB_REPO_NAME="${DAGSHUB_REPO_NAME:-networksecurity}"
DVC_REMOTE_NAME="${DVC_REMOTE_NAME:-origin}"

if ! command -v dvc >/dev/null 2>&1; then
  echo "dvc is not installed. Install it first (pip install dvc)."
  exit 1
fi

if [[ -z "${DAGSHUB_USER:-}" || -z "${DAGSHUB_TOKEN:-}" ]]; then
  echo "Set DAGSHUB_USER and DAGSHUB_TOKEN before running this script."
  exit 1
fi

if [[ ! -d ".dvc" ]]; then
  dvc init
fi

REMOTE_URL="${DAGSHUB_BASE_URL}/${DAGSHUB_REPO_OWNER}/${DAGSHUB_REPO_NAME}.dvc"
ENDPOINT_URL="${DAGSHUB_BASE_URL}/${DAGSHUB_REPO_OWNER}/${DAGSHUB_REPO_NAME}.s3"

if dvc remote list | awk '{print $1}' | grep -qx "${DVC_REMOTE_NAME}"; then
  dvc remote remove "${DVC_REMOTE_NAME}"
fi

dvc remote add "${DVC_REMOTE_NAME}" "${REMOTE_URL}"
dvc remote modify "${DVC_REMOTE_NAME}" endpointurl "${ENDPOINT_URL}"
dvc remote modify --local "${DVC_REMOTE_NAME}" auth basic
dvc remote modify --local "${DVC_REMOTE_NAME}" user "${DAGSHUB_USER}"
dvc remote modify --local "${DVC_REMOTE_NAME}" password "${DAGSHUB_TOKEN}"

echo "DVC remote '${DVC_REMOTE_NAME}' configured for ${DAGSHUB_REPO_OWNER}/${DAGSHUB_REPO_NAME}."
