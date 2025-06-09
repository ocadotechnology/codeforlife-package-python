"""
© Ocado Group
Created on 29/11/2024 at 15:59:40(+00:00).

This file contains all the variables required and/or exposed by Ocado's
Technology Platform.

NOTE: All variables should be retrieved like so: `os.getenv("key")`.
"""

import os

# App

APP_ID = os.getenv("APP_ID")
APP_VERSION = os.getenv("APP_VERSION")

# AWS

AWS_REGION = os.getenv("aws_region")

# AWS S3

AWS_S3_APP_BUCKET = os.getenv("aws_s3_app_bucket")
AWS_S3_APP_FOLDER = os.getenv("aws_s3_app_folder")
AWS_S3_APP_DOMAIN = f"{AWS_S3_APP_BUCKET}.s3.amazonaws.com"
AWS_S3_APP_DEFAULT_ACL = os.getenv("AWS_S3_APP_DEFAULT_ACL")
AWS_S3_APP_QUERYSTRING_AUTH = bool(
    int(os.getenv("AWS_S3_APP_QUERYSTRING_AUTH", "1"))
)
AWS_S3_APP_QUERYSTRING_EXPIRE = int(
    os.getenv("AWS_S3_APP_QUERYSTRING_EXPIRE", "3600")
)
AWS_S3_STATIC_BUCKET = os.getenv("AWS_S3_STATIC_BUCKET")
AWS_S3_STATIC_FOLDER = os.getenv("AWS_S3_STATIC_FOLDER")
AWS_S3_STATIC_DOMAIN = f"{AWS_S3_STATIC_BUCKET}.s3.amazonaws.com"
AWS_S3_STATIC_DEFAULT_ACL = os.getenv("AWS_S3_STATIC_DEFAULT_ACL")
AWS_S3_STATIC_QUERYSTRING_AUTH = bool(
    int(os.getenv("AWS_S3_STATIC_QUERYSTRING_AUTH", "1"))
)
AWS_S3_STATIC_QUERYSTRING_EXPIRE = int(
    os.getenv("AWS_S3_STATIC_QUERYSTRING_EXPIRE", "3600")
)

# RDS

RDS_DB_NAME = os.getenv("RDS_DB_NAME")
RDS_SCHEMA_NAME = os.getenv("RDS_SCHEMA_NAME")
RDS_INSTANCE_NAME = os.getenv("RDS_INSTANCE_NAME")
RDS_DB_DATA_PATH = (
    f"{AWS_S3_APP_FOLDER}/dbMetadata/"
    + (f"{RDS_INSTANCE_NAME}/" if RDS_INSTANCE_NAME else "")
    + f"{RDS_DB_NAME}/{RDS_SCHEMA_NAME}.dbdata"
)

# ElastiCache

CACHE_CLUSTER_ID = os.getenv("CACHE_CLUSTER_ID")
CACHE_DB_DATA_PATH = (
    f"{AWS_S3_APP_FOLDER}/elasticacheMetadata/{CACHE_CLUSTER_ID}.dbdata"
)

# SQS

SQS_URL = os.getenv("SQS_URL")
