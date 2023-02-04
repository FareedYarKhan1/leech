import boto3
from botocore.exceptions import NoCredentialsError
import datetime
from django.contrib.auth.models import User



ACCESS_KEY = 'AKIARPPQWUWXQJGAVPSZ'
SECRET_KEY = '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'
BUKET_NAME= "cs181106"

'''
A function upload the local generated label pdf to aws s3 buket
:param filename str: local label pdf file path
.
.
.
:return str : url of uploaded file on s3

'''
def upload_to_aws(local_filename,file_name):
    
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    try:
        folder="scrappingResult/"
        s3.upload_file(local_filename,BUKET_NAME, folder+file_name)
        url=f"https://{BUKET_NAME}.s3.ap-south-1.amazonaws.com/{folder}{file_name}"
        return url
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False


