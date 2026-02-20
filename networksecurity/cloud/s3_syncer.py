import os
import shutil
import subprocess
import sys
import time

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.constant.training_pipeline import (
    AWS_SYNC_MAX_RETRIES,
    AWS_SYNC_RETRY_DELAY_SECONDS,
    AWS_SYNC_TIMEOUT_SECONDS,
    ENABLE_S3_BUCKET_CHECK,
)


class S3Sync:
    def __init__(self) -> None:
        if shutil.which("aws") is None:
            raise NetworkSecurityException("AWS CLI is not installed or not in PATH.", sys)

    @staticmethod
    def _extract_bucket_root(aws_bucket_url: str) -> str:
        if not aws_bucket_url.startswith("s3://"):
            raise NetworkSecurityException(f"Invalid S3 URL: {aws_bucket_url}", sys)
        bucket_and_path = aws_bucket_url.replace("s3://", "", 1)
        bucket = bucket_and_path.split("/", 1)[0].strip()
        if not bucket:
            raise NetworkSecurityException(f"Invalid S3 bucket in URL: {aws_bucket_url}", sys)
        return f"s3://{bucket}"

    def _run_aws_command(self, command: list[str], operation_name: str) -> None:
        attempt = 1
        while attempt <= AWS_SYNC_MAX_RETRIES:
            try:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=AWS_SYNC_TIMEOUT_SECONDS,
                    check=True,
                )
                if result.stdout.strip():
                    logging.info(result.stdout.strip())
                return
            except subprocess.CalledProcessError as e:
                stderr = (e.stderr or "").strip()
                stdout = (e.stdout or "").strip()
                logging.error(
                    f"{operation_name} failed on attempt {attempt}/{AWS_SYNC_MAX_RETRIES}. "
                    f"exit_code={e.returncode} stdout={stdout} stderr={stderr}"
                )
                if attempt == AWS_SYNC_MAX_RETRIES:
                    raise NetworkSecurityException(
                        f"{operation_name} failed after {AWS_SYNC_MAX_RETRIES} attempts: {stderr or stdout}",
                        sys,
                    )
                time.sleep(AWS_SYNC_RETRY_DELAY_SECONDS)
                attempt += 1
            except subprocess.TimeoutExpired as e:
                logging.error(
                    f"{operation_name} timed out on attempt {attempt}/{AWS_SYNC_MAX_RETRIES} "
                    f"after {AWS_SYNC_TIMEOUT_SECONDS}s."
                )
                if attempt == AWS_SYNC_MAX_RETRIES:
                    raise NetworkSecurityException(
                        f"{operation_name} timed out after {AWS_SYNC_MAX_RETRIES} attempts.",
                        sys,
                    )
                time.sleep(AWS_SYNC_RETRY_DELAY_SECONDS)
                attempt += 1
            except Exception as e:
                raise NetworkSecurityException(e, sys)

    def _verify_bucket_access(self, aws_bucket_url: str) -> None:
        if not ENABLE_S3_BUCKET_CHECK:
            return
        bucket_root = self._extract_bucket_root(aws_bucket_url=aws_bucket_url)
        command = ["aws", "s3", "ls", bucket_root]
        self._run_aws_command(command=command, operation_name=f"Bucket check for {bucket_root}")

    def sync_folder_to_s3(self, folder: str, aws_bucket_url: str) -> None:
        if not os.path.isdir(folder):
            raise NetworkSecurityException(f"Local folder does not exist: {folder}", sys)
        self._verify_bucket_access(aws_bucket_url=aws_bucket_url)
        command = ["aws", "s3", "sync", folder, aws_bucket_url]
        self._run_aws_command(command=command, operation_name=f"S3 upload {folder} -> {aws_bucket_url}")

    def sync_folder_from_s3(self, folder: str, aws_bucket_url: str) -> None:
        os.makedirs(folder, exist_ok=True)
        self._verify_bucket_access(aws_bucket_url=aws_bucket_url)
        command = ["aws", "s3", "sync", aws_bucket_url, folder]
        self._run_aws_command(command=command, operation_name=f"S3 download {aws_bucket_url} -> {folder}")
