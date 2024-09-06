import itertools
import uuid
from typing import List

from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import HTMLResponse

import methods
import db_methods


from db_methods import add_information_about_group_send_alchemy, update_count_of_buckets
from settings import client as cl


app = FastAPI()



@app.post("/frames/")
async def create_upload_files(files: List[UploadFile]):
    """
    Функция сохраняет переданные файлы в корзину с именем <дата в формате YYYYMMDD>
    объектного хранилища min.io с именами <UUID>.jpg
    и фиксирует в базе данных в таблице inbox со структурой:
    <код запроса> | <имя сохраненного файла> | <дата / время регистрации> \n
    :param files: полученные файлы \n
    :return: возвращает перечень созданных элементов в формате JSON
    """
    methods.check_files(files)  # Проверка количества и MIME-типа файлов
    number_bucket = methods.get_bucket_name()  # получение названия корзины
    print(f'Номер корзины: {number_bucket}')
    check_bucket = cl.bucket_exists(number_bucket)
    if not check_bucket:
        cl.make_bucket(number_bucket)
        print(f'Создана {number_bucket}')
        methods.create_bucket(number_bucket)  # создание корзины
        add_information_about_group_send_alchemy(number_bucket)
    bucket_id = db_methods.get_bucket_info_alchemy(number_bucket)
    print(f'bucket_id: {bucket_id}')
    req_id = db_methods.create_request_number_alchemy(bucket_id)
    print(f'req_id: {req_id}')
    files_dict = {"bucket_id": bucket_id,
                  "bucket_name": number_bucket,
                  "req_id": req_id}
    number_file = itertools.count(1)  # генератор порядкового номера файла для ключа словаря
    for file in files:
        meta_name = file.filename.split('.')[-1]
    #     # file_name = f'{uuid.uuid4()}.jpg'  # генерируем UUID название файла
        file_name = f'{uuid.uuid4()}.{meta_name}'  # файл с тем же разрешением
        contents = await file.read()
        methods.add_files(file_name, contents, number_bucket)  # засылаем файлы в корзину
        if db_methods.create_info_about_file_to_db_alchemy(request_number=req_id, file_name=file_name):
        # записываем информацию о загрузке в таблицу inboxfiles
            num_key = f'File number {next(number_file)}'
            files_dict[num_key] = file_name
    return files_dict
    # return number_bucket



@app.get("/frames/{item_id}")
async def read_files(item_id: int):
    """
    На вход подается код запроса. На выходе возвращается список соответствующих коду запроса изображений
    в формате JSON, включая дату и время регистрации и имена файлов.\n
    :param item_id: Код запроса \n
    :return: JSON строка
    """
    result = db_methods.get_file_list_from_db_alchemy(item_id)  # получаем из таблицы inbox файлы по номеру запроса
    return result


@app.delete("/frames/{item_id}")
async def delete_files(item_id: int):
    """
    Функция удаляет данные по запросу из базы данных
    и соответствующие файлы изображений из объектного хранилища.
    :param item_id: номер запроса req
    :return:
    """
    files_list = db_methods.get_file_from_db(item_id)  # получаем из таблицы inbox файлы по номеру запроса
    del_files = methods.delete_files_from_bucket(files_list)  # удаляем из корзины файлы
    files_dict = {"delete_request_number": item_id}
    if len(files_list) != 0:
        db_methods.delete_req_from_db(item_id)  # удаляем файлы из базы данных
        files_dict['delete_status'] = f'{HTTPException(200)}'
        files_dict['detail'] = "Ok"
    else:
        return HTTPException(404, detail="Not found in DB")  # при отсутствии записей в базе данных
    files_dict['files'] = del_files
    return files_dict


@app.get("/")
async def main():
    content = """
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
    <body>
        <div class="container text-center">
        <h2 class="m-3">Загрузите файлы</h2>
            <form action="/frames/" enctype="multipart/form-data" method="post">
              <input name="files" type="file" class="form-control" id="inputGroupFile01" multiple> <br>
              <input class="btn btn-outline-secondary" type="submit">
            </form>
        </div>
    </body>
    """
    return HTMLResponse(content=content)

# @app.get("/test")
# async def test():
#     # methods.check_files(files)  # Проверка количества файлов
#     number_bucket = methods.get_bucket_name()  # получение названия корзины
#     # number_bucket = '2024095'  # получение названия корзины
#     check_bucket = cl.bucket_exists(number_bucket)
#     if not check_bucket:
#         cl.make_bucket(number_bucket)
#         print(f'Создана {number_bucket}')
#         methods.create_bucket(number_bucket)  # создание корзины
#         add_information_about_group_send_alchemy(number_bucket)
#     bucket_id = db_methods.get_bucket_info_alchemy(number_bucket)
#     print(f'bucket_id: {bucket_id}')
#     req_id = db_methods.create_request_number_alchemy(bucket_id)
#     print(f'req_id: {req_id}')
#     return HTMLResponse(status_code=200)
