from storages.backends.s3boto3 import S3Boto3Storage


class PrivateMediaStorage(S3Boto3Storage):
    location = "assets"
    default_acl = "private"
    file_overwite = False
    custom_domain = False
