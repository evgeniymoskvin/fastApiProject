from minio import Minio
"""
Данные для отправки данных на min.io
"""

client = Minio(
    "45.132.18.6:9000",
    access_key="uVwUzCeMtpXECCEJBTyT",
    secret_key="JKjqTqm3nXeK6VwQLmV8lEx3Xnmgt0wn5z4lFi9K",
    secure=False
)
