import os
import itertools
from datetime import datetime

import minio.error
from fastapi import HTTPException

from settings import client as cl


def get_bucket_name() -> str:
    """
    Функция с помощью datetime генерирует название корзины для min.io
    :return: Строка с названием корзины
    """
    today = datetime.today()
    return f'{today.year}{str(today.month).rjust(2, "0")}{str(today.day).rjust(2, "0")}'


def create_bucket(found: str, client=cl):
    """
    Принимает строку с названием, проверяет существование корзины с таким названием
    и при необходимости создает корзину
    :param client:  client min.io
    :param found: Название корзины
    """
    check_bucket = client.bucket_exists(found)
    if not check_bucket:
        client.make_bucket(found)


def check_files(files: list):
    """
    Проверяет входящие файлы. Их количество (от 1 до 15) и content type
    :param files: список файлов
    """
    if len(files) > 15 or len(files) == 0:
        raise HTTPException(400, detail="Много файлов")
    elif len(files) == 0:
        raise HTTPException(400, detail="Файлы отсутствуют")


def add_files(file_name: str, contents: bytes, number_bucket: str, client=cl):
    """
    Функция создает временный файл для отправки его в корзину min.io
    После отправки временный файл удаляется
    :param client: client min.io
    :param file_name: название файла
    :param contents: содержимое файла
    :param number_bucket:  название корзины
    :return:
    """
    with open(file_name, 'wb') as f:
        f.write(contents)  # создаем временный файл, для отправки в корзину
    client.fput_object(f'{number_bucket}', f"{file_name}", f"{file_name}")
    os.remove(file_name)  # удаляем временный файл


def delete_files_from_bucket(files_dict: dict, client=cl) -> dict:
    """
    Функция удаляет файлы из корзины
    :param client: client min.io
    :param files_dict: словарь с информацией об удалении
    :return: словарь с результатами работы функции.
    """
    number_file = itertools.count(1)
    result_dict = {}  # словарь с удаленными файлами
    result_dict['bucket_id'] = files_dict['bucket_id']
    result_dict['bucket_name'] = files_dict['bucket_name']
    for key, file_name in files_dict['files'].items():
        if client.bucket_exists(files_dict['bucket_name']):  # проверяем существование корзины
            try:  # Отлавливаем ошибку, если файл был удален из корзины, но остался в бд
                client.get_object(files_dict['bucket_name'], file_name)
                client.remove_object(files_dict['bucket_name'], file_name)
                result_dict[number_file] = {"file name": file_name}
            except minio.error.S3Error:
                result_dict[number_file] = {"errors": f"Файл {file_name} не найден в хранилище"}
        else:
            result_dict['error'] = {f'Bucket not found'}
    # for obj in files_list:
    #     number_bucket = obj[2]  # название корзины из таблицы
    #     date_reg = obj[1]  # дата регистрации файла из таблицы
    #     file_name = obj[0]  # название файла из таблицы
    #     num_key = f'File number {next(number_file)}'
    #     if client.bucket_exists(number_bucket):  # проверяем существование корзины
    #         try:  # Отлавливаем ошибку, если файл был удален из корзины, но остался в бд
    #             client.get_object(number_bucket, file_name)
    #             client.remove_object(number_bucket, file_name)
    #             files_dict[num_key] = {"file name": file_name,
    #                                    "date_reg": date_reg}
    #         except minio.error.S3Error:
    #             files_dict[num_key] = {"errors": f"Файл {file_name} не найден в хранилище"}
    return result_dict
