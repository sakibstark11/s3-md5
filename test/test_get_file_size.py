from typing import Tuple

from boto3 import Session
from mypy_boto3_s3 import S3Client

from s3_md5 import get_file_size


def test_get_file_size(s3_setup: Tuple[Session, S3Client, str, str, str]):
    _, s3_client, test_bucket, test_file_name, test_body = s3_setup
    file_size = get_file_size(s3_client, test_bucket, test_file_name)
    assert file_size == len(test_body)
