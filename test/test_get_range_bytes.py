from typing import Tuple

from boto3 import Session
from mypy_boto3_s3 import S3Client

from s3_md5 import get_range_bytes


def test_get_range_bytes(s3_setup: Tuple[Session, S3Client, str, str, str]):
    _, s3_client, test_bucket, test_file_name, test_body = s3_setup
    range_string = 'bytes=0-0'
    data = get_range_bytes(s3_client,
                           test_bucket,
                           test_file_name,
                           range_string)
    assert data == bytes(test_body[0], 'utf-8')
