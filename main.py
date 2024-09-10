import itertools
import uuid
import logging
from typing import List

import db_methods
import methods
from fastapi import FastAPI, UploadFile
from settings import client as cl

app = FastAPI()
logging.basicConfig(level=logging.INFO, filename='py_log.log', filemode='w')

@app.post("/frames/")
async def create_upload_files(files: List[UploadFile]) -> dict:
    """
    Сохраняем переданные файлы в корзину min.io
    Имя корзины: <дата в формате YYYYMMDD>
    объектного хранилища min.io с именами <UUID>.***
    и фиксирует в базе данных в таблице inboxfiles и requests_number:
    """
    number_bucket = methods.get_bucket_name()  # получение названия корзины
    logging.info(f"Номер корзины: {number_bucket}")
    check_bucket = cl.bucket_exists(number_bucket)  # Проверяем есть ли корзина
    if not check_bucket:
        cl.make_bucket(number_bucket)
        logging.info(f"Создана корзина: {number_bucket}")
        methods.create_bucket(number_bucket)  # создание корзины
        db_methods.add_information_about_group_send_alchemy(number_bucket)
    bucket_id = db_methods.get_bucket_info_alchemy(number_bucket)
    req_id = db_methods.create_request_number_alchemy(bucket_id)
    files_dict = {"bucket_id": bucket_id, "bucket_name": number_bucket, "req_id": req_id}
    # генератор порядкового номера файла для ключа словаря
    number_file = itertools.count(1)
    for file in files:
        meta_name = file.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{meta_name}"  # файл с тем же разрешением
        contents = await file.read()
        # засылаем файлы в корзину
        methods.add_files(file_name, contents, number_bucket)
        if db_methods.create_info_about_file_to_db_alchemy(
            request_number=req_id, file_name=file_name
        ):
            # записываем информацию о загрузке в таблицу InboxFiles
            num_key = f"File number {next(number_file)}"
            files_dict[num_key] = file_name
    return files_dict
    # return number_bucket


@app.get("/frames/{item_id}")
async def read_files(item_id: int) -> dict:
    """
    Получение списка файлов по номеру отправки
    """
    # получаем из таблицы inbox файлы по номеру запроса
    result = db_methods.get_file_list_from_db_alchemy(item_id)
    return result


@app.get("/buckets")
async def get_buckets_list():
    """
    Получения списка всех корзин
    """
    buckets = methods.get_all_buckets_list()
    number_file = itertools.count(1)
    buckets_dict = {}
    for bucket in buckets:
        buckets_dict[next(number_file)] = bucket
    result = {"buckets": buckets_dict}
    return result


@app.delete("/frames/{item_id}")
async def delete_files(item_id: int) -> dict:
    """
    Удаление данных из базы данных
    и соответствующих файлов из min.io.
    """
    # получаем из таблицы inbox файлы по номеру запроса
    files_list = db_methods.get_file_list_from_db_alchemy(item_id)
    # удаляем из корзины файлы
    del_files_bucket = methods.delete_files_from_bucket(files_list)
    del_files_db = db_methods.delete_file_list_from_db_alchemy(item_id)
    result_dict = {
        "files": del_files_bucket,
        "db": del_files_db,
    }
    return result_dict
