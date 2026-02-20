import os
from typing import Optional

import dagshub
import mlflow
from dagshub.streaming import install_hooks
from dagshub.upload import Repo
from dotenv import load_dotenv

from networksecurity.constant.training_pipeline import (
    DAGSHUB_REPO_OWNER,
    DAGSHUB_REPO_NAME,
    DEFAULT_MLFLOW_TRACKING_URI,
)

load_dotenv()

_HOOKS_INSTALLED = False
_MLFLOW_INITIALIZED = False


def initialize_mlflow() -> str:
    """
    Configure DagsHub + remote MLflow tracking once per process.
    """
    global _HOOKS_INSTALLED
    global _MLFLOW_INITIALIZED

    if not _HOOKS_INSTALLED:
        install_hooks()
        _HOOKS_INSTALLED = True

    if not _MLFLOW_INITIALIZED:
        dagshub.init(repo_owner=DAGSHUB_REPO_OWNER, repo_name=DAGSHUB_REPO_NAME, mlflow=True)
        _MLFLOW_INITIALIZED = True

    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", DEFAULT_MLFLOW_TRACKING_URI)
    mlflow.set_tracking_uri(tracking_uri)
    return tracking_uri


def upload_to_dagshub(local_path: str, remote_path: str, versioning: str = "dvc") -> None:
    """
    Optional helper to upload artifacts/files to DagsHub.
    Auth is handled by environment/session; no credentials are stored in code.
    """
    repo = Repo(DAGSHUB_REPO_OWNER, DAGSHUB_REPO_NAME)
    repo.upload(local_path=local_path, remote_path=remote_path, versioning=versioning)


def get_tracking_uri() -> Optional[str]:
    return mlflow.get_tracking_uri()
