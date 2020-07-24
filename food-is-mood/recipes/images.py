import boto3, os, sys, uuid

AWS_S3_BUCKET_NAME = os.environ['AWS_S3_BUCKET_NAME']
BASE_PATH = os.environ['AWS_S3_BASE_PATH']
VALID_FILE_EXTENSIONS = [ '.jpg', '.jpeg', '.png', '.gif' ]
UPLOAD_ARGS = {
    "ACL": 'public-read'
}

def _get_s3_resource():
    bucket_name = AWS_S3_BUCKET_NAME
    session = boto3.Session(aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'], aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
    return session.resource('s3')

def _verify_image(image):
    # check filesize
    # check mimetype

    # check extension
    filename, file_extension = os.path.splitext(image['filename'])

    if filename is None or file_extension not in VALID_FILE_EXTENSIONS:
        raise Exception('Incorrect filename or filetype')

    return file_extension

def delete_image(url):
    if url is None:
        return

    if os.path.isdir(url):
        raise Exception('Attempting to delete path')

    s3 = _get_s3_resource()
    image = s3.Object(AWS_S3_BUCKET_NAME, url)
    image.delete()
    print('>> Deleted image: {}'.format(url))

def upload_image(image):
    file_extension = _verify_image(image)
    s3 = _get_s3_resource()

    filename = uuid.uuid4().hex + file_extension
    file = os.path.join(BASE_PATH, filename)

    config = boto3.s3.transfer.TransferConfig(use_threads=True, max_concurrency=1)
    response = s3.meta.client.upload_fileobj(image['fp'], AWS_S3_BUCKET_NAME, file, ExtraArgs=UPLOAD_ARGS, Config=config)

    object_acl = s3.ObjectAcl(AWS_S3_BUCKET_NAME, file)
    object_acl.put(ACL='public-read')        
    print('>> Uploaded image: {}'.format(file))

    return file
