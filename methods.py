import os
import itertools
from datetime import datetime

import minio.error

from settings import client as cl


def get_all_buckets_list():
    return cl.list_buckets()


def get_bucket_name() -> str:
    """
    Генерация название корзины для min.io
    """
    today = datetime.today()
    return f'{today.year}{str(today.month).rjust(2, "0")}{str(today.day).rjust(2, "0")}'


def create_bucket(found: str, client=cl):
    """
    Проверяет существование корзины с полученным названием
    и при необходимости создает корзину
    """
    check_bucket = client.bucket_exists(found)
    if not check_bucket:
        client.make_bucket(found)


def add_files(file_name: str, contents: bytes, number_bucket: str, client=cl):
    """
    Добавление файла в min.io
    """
    with open(file_name, 'wb') as f:
        f.write(contents)  # создаем временный файл, для отправки в корзину
    client.fput_object(f'{number_bucket}', f"{file_name}", f"{file_name}")
    os.remove(file_name)  # удаляем временный файл


def delete_files_from_bucket(files_dict: dict, client=cl) -> dict:
    """
    Удаляет файлы из корзины min.io
    """
    number_file = itertools.count(1)
    result_dict = {
        'bucket_id': files_dict['bucket_id'],
        'bucket_name': files_dict['bucket_name']
    }
    for key, file_name in files_dict['files'].items():
        if client.bucket_exists(files_dict['bucket_name']):  # проверяем существование корзины
            try:  # Отлавливаем ошибку, если файл был удален из корзины, но остался в бд
                client.get_object(files_dict['bucket_name'], file_name)
                client.remove_object(files_dict['bucket_name'], file_name)
                result_dict[next(number_file)] = file_name
            except minio.error.S3Error:
                result_dict[next(number_file)] = {"errors": f"Файл {file_name} не найден в хранилище"}
        else:
            result_dict['error'] = {f'Bucket not found'}
    return result_dict
