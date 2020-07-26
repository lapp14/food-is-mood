import boto3, os, sys, uuid

AWS_S3_BUCKET_NAME = os.environ['AWS_S3_BUCKET_NAME']
BASE_PATH = os.environ['AWS_S3_BASE_PATH']
VALID_FILE_EXTENSIONS = [ '.jpg', '.jpeg', '.png', '.gif' ]
MIN_FILESIZE_BYTES = 15360   # 15 kb
MAX_FILESIZE_BYTES = 15728640   # 15 Mb
UPLOAD_ARGS = {
    "ACL": 'public-read'
}

ERROR_TEXT = dict(
    max_filesize="Files must be under {} Mb".format(MAX_FILESIZE_BYTES / 1024 / 1024),
    min_filesize="Files must be at least {} kb".format(MIN_FILESIZE_BYTES / 1024),
    missing_filename="Incorrect filename or filetype",
    invalid_extension="Valid filetypes are {}".format(VALID_FILE_EXTENSIONS),
    attempt_delete_path='Attempting to delete path'
)
    


def _get_s3_resource():
    bucket_name = AWS_S3_BUCKET_NAME
    session = boto3.Session(aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
    return session.resource('s3')

def _check_file_extension(image):
    filename, file_extension = os.path.splitext(image['filename'])

    if filename is None:
        raise Exception(ERROR_TEXT.missing_filename)

    if file_extension not in VALID_FILE_EXTENSIONS:
        raise Exception(ERROR_TEXT.invalid_extension)

    return file_extension

def _get_stream_filesize(filestream):
    filesize = filestream.seek(0, 2)
    filestream.seek(0, 0)
    return filesize

def verify_image(image):
    # check filesize
    filesize = _get_stream_filesize(image['fp'])
    if filesize < MIN_FILESIZE_BYTES:
        raise Exception(ERROR_TEXT.min_filesize)
    
    if filesize > MAX_FILESIZE_BYTES:
        raise Exception(ERROR_TEXT.max_filesize)

    # check mimetype

    # check extension and return
    return _check_file_extension(image)

def delete_image(url):
    if url is None:
        return

    if os.path.isdir(url):
        raise Exception(ERROR_TEXT.attempt_delete_path)

    s3 = _get_s3_resource()
    image = s3.Object(AWS_S3_BUCKET_NAME, url)
    image.delete()
    print('>> Deleted image: {}'.format(url))

def upload_image(image):
    print('UPLOAD IMAGE')
    file_extension = _check_file_extension(image)
    s3 = _get_s3_resource()

    filename = uuid.uuid4().hex + file_extension
    file = os.path.join(BASE_PATH, filename)

    config = boto3.s3.transfer.TransferConfig(use_threads=True, max_concurrency=1)
    response = s3.meta.client.upload_fileobj(image['fp'], AWS_S3_BUCKET_NAME, file, ExtraArgs=UPLOAD_ARGS, Config=config)

    object_acl = s3.ObjectAcl(AWS_S3_BUCKET_NAME, file)
    object_acl.put(ACL='public-read')        
    print('>> Uploaded image: {}'.format(file))

    return file
