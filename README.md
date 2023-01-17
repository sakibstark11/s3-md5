# s3-md5
Get fast md5 hashes for an s3 file.
## installation
- python 3.10
- boto3
- boto3-stubs[all]

## how to use

### threaded
Uses threads to fetch chunks.

From the command line run
```
python s3_md5.py <bucket_name> <file_name>
```
There are two *optional* arguments that you may want to provide
- `-w` or workers sets the number of python threads to use for downloading purposes, by default its set to the following equation `number of cpu cores * 2 - 1`
- `-c` or chunk_size in ***bytes*** sets the individual download size on each get request sent to s3, by default its set to `1000000` bytes.

#### caveats
- File size can not be smaller than the default chunk size of `1000000`, if yes, then the chunk size must be manually provided or it will raise an assertion error.

### async
Fetches the chunks in an async manner.

From the command line run
```
python async_s3_md5.py <bucket_name> <file_name>
```
There is one *optional* arguments that you may want to provide
- `-c` or chunk_size in ***bytes*** sets the individual download size on each get request sent to s3, by default its set to `1000000` bytes.

#### caveats
- File size can not be smaller than the default chunk size of `1000000`, if yes, then the chunk size must be manually provided or it will raise an assertion error.
- No tests added.
