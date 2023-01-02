'''module uses threads to download file from s3 and generates md5 hash'''
import logging
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from hashlib import md5
from multiprocessing import cpu_count
from time import perf_counter

from boto3 import client
from mypy_boto3_s3 import S3Client


def get_file_size(s3_client: S3Client,
                  bucket: str,
                  file_name: str,
                  ) -> int:
    '''makes a head object request to get file size in bytes'''
    s3_object = s3_client.head_object(Bucket=bucket,
                                      Key=file_name)
    return s3_object['ContentLength']


def calculate_range_bytes_from_part_number(part_number: int,
                                           chunk_size: int,
                                           file_size: int,
                                           file_chunk_count: int) -> str:
    '''
        calculates the byte range to fetch
        starts from 0 if its the first iteration
        if not the first iteration; part number * chunk size
        uses remaining file length if its the last iteration
        if not; (( part number * chunk size ) + chunk size ) - 1
    '''
    start_bytes: int = (part_number * chunk_size) if part_number != 0 else 0

    end_bytes: int = file_size if part_number + \
        1 == file_chunk_count else (((part_number * chunk_size) + chunk_size) - 1)
    return f'bytes={start_bytes}-{end_bytes}'


def get_range_bytes(s3_client: S3Client,
                    bucket: str,
                    file_name: str,
                    part_number: int,
                    chunk_size: int,
                    file_size: int,
                    file_chunk_count: int) -> bytes:
    '''fetches the range bytes requested from s3'''
    range_string = calculate_range_bytes_from_part_number(
        part_number, chunk_size, file_size, file_chunk_count)

    logging.debug(
        f'part number {part_number + 1} downloading bytes {range_string}')
    body = s3_client.get_object(Bucket=bucket,
                                Key=file_name,
                                Range=range_string)['Body'].read()
    logging.debug(
        f'part number {part_number + 1} downloaded bytes {range_string}')

    return body


def parse_file_md5(s3_client: S3Client,
                   bucket: str,
                   file_name: str,
                   chunk_size: int,
                   workers: int) -> str:
    '''main function to orchestrate the md5 generation of s3 object'''
    file_size = get_file_size(s3_client, bucket, file_name)
    if file_size < chunk_size:
        raise AssertionError('file size cannot be smaller than chunk size')
    logging.info(f'file size {file_size}')
    file_chunk_count = file_size // chunk_size
    logging.info(f'file chunk count {file_chunk_count}')

    with ThreadPoolExecutor(max_workers=workers) as thread_executor:
        results = thread_executor.map(
            lambda part_number: get_range_bytes(
                s3_client,
                bucket,
                file_name,
                part_number,
                chunk_size,
                file_size,
                file_chunk_count),
            range(file_chunk_count))

        hash_object = md5()

        logging.info('downloading')
        for result in results:
            hash_object.update(result)

        return hash_object.hexdigest()


def parse_args():
    '''parses command line arguments'''
    DEFAULT_WORKERS = cpu_count() * 2 - 1
    DEFAULT_CHUNK_SIZE = 1000000

    parser = ArgumentParser(description='parse md5 of an s3 object')
    parser.add_argument('bucket',
                        type=str,
                        help='bucket name')
    parser.add_argument('file_name',
                        help='file name',
                        type=str)
    parser.add_argument('-w', '--workers', type=int,
                        default=DEFAULT_WORKERS,
                        help='number of cpu threads to use for downloading')
    parser.add_argument('-c', '--chunk_size', type=int,
                        default=DEFAULT_CHUNK_SIZE,
                        help='chunk size to download on each request')
    return parser.parse_args()


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s %(levelname)s: %(message)s',
        level=logging.INFO,
        datefmt='%d-%m-%Y %H:%M:%S')

    start_time = perf_counter()

    args = parse_args()
    main_s3_client = client("s3")
    md5_hash = parse_file_md5(
        main_s3_client,
        args.bucket,
        args.file_name,
        args.chunk_size,
        args.workers
    )
    logging.info(f'md5 hash: {md5_hash}')

    logging.info(f'took {perf_counter() - start_time} seconds')
