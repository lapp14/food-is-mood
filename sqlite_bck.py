import datetime
import os
import string
import tarfile
import shutil
import boto3
from boto3.s3.connection import S3Connection
from boto3.s3.key import Key
from datetime import timedelta

# Configuration inlcudes of AWS credentials, db.sqlite3 file and local backup path
# note: first you need to store this script where your db.sqlite3 db is located
# Then you can run the script "python sqlite_bck.py

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
s3 = S3Connection(aws_access_key, aws_secret_key)
bucket = s3.get_bucket(aws_bucket)

# Send files to S3
print ('[S3] Uploading file archive ' + full_archive_name + '...')
k = Key(bucket)
k.key = aws_folder + '/' + today + '/' + full_archive_name
print(k.key)
k.set_contents_from_filename(full_archive_file_path)
k.set_acl("public-read")
# os.system(cmd)

print('[S3] Clearing previous file archive ' + full_archive_name + '...')
shutil.rmtree(path)
print('Removed backup of Local database')
