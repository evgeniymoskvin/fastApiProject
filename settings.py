from minio import Minio

"""
Данные для отправки данных на min.io
Надо вынести в переменную окружения, 
Оставлена здесь, для проверки
"""
client = Minio(
    "194.87.99.84:9000",
    access_key="DJxkijWpi9zI9Qm5",
    secret_key="SfIpv9R98IOBM87ETYuPcATe59BByp7K",
    secure=False
)

