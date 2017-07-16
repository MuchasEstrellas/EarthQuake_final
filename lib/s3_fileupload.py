import boto
import os.path
from flask import current_app as app



def s3_fileupload(file):

    if upload_dir is None:
        upload_dir = app.config["S3_UPLOAD_DIRECTORY"]

    file_name = os.path.splitext(file.data.filename)[0]
    source_extension = os.path.splitext(file.data.filename)[1]

    destination_filename = file_name + source_extension

    # Connect to S3 and upload file.
    conn = boto.connect_s3(app.config["AWS_ACCESS_KEY_ID"], app.config["AWS_SECRET_ACCESS_KEY"])
    b = conn.get_bucket(app.config["FLASKS3_BUCKET_NAME"])

    sml = b.new_key("/".join(["static/uploadedfiles", destination_filename]))
    sml.set_contents_from_string(source_file.data.read())
    sml.set_acl("public-read")

    return destination_filename
