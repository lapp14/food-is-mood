import datetime
import os
import string
import tarfile
import shutil
import boto3
from botocore.exceptions import ClientError
from datetime import timedelta

# Configuration inlcudes of AWS credentials, db.sqlite3 file and local backup path
# note: first you need to store this script where your db.sqlite3 db is located
# Then you can run the script "python sqlite_bck.py

ARGS = {
    'ACL': 'private'
}

aws_access_key = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_key = os.environ['AWS_SECRET_ACCESS_KEY']
aws_bucket = 'food-is-mood'
aws_folder = 'backups'

## create directory inside /tmp and backup the database
os.system("mkdir /tmp/backup_db")
path='/tmp/backup_db/'
db="recipes.sqlite"

cmd= "sqlite3 recipes.sqlite .dump > '"+path+"''"+db+"'"
os.system(cmd)

#configuring filepath and tar file name
today = str(datetime.date.today())
archieve_name = db
db_path = path + db
archieve_path = path + archieve_name

print('[FILE] Creating archive for ' + db)
shutil.make_archive(archieve_path, 'gztar', path)
print('Completed archiving database')
full_archive_file_path = archieve_path + ".tar.gz"
full_archive_name = archieve_name + ".tar.gz"

# Establish S3 Connection
# s3 = boto3.resource('s3')
# bucket = s3.bucket(aws_bucket) # bucket = s3.get_bucket(aws_bucket)

# Send files to S3
print ('[S3] Uploading file archive ' + full_archive_name + '...')
archive_path = aws_folder + '/' + today + '/' + full_archive_name

s3 = boto3.client('s3')
with open(full_archive_file_path, "rb") as f:
    response = s3.upload_fileobj(f, aws_bucket, archive_path, ExtraArgs=ARGS)
    print(response)

print('[S3] Clearing previous file archive ' + full_archive_name + '...')
shutil.rmtree(path)
print('Removed backup of Local database')
