from datetime import datetime
import unittest
import os

from starlette import datastructures
from fastapi import HTTPException
import minio
import sqlite3
import requests


from settings import client
from fastapi import UploadFile

import methods
import db_methods

db = sqlite3.connect('tests/test_db.sqlite')  # подключение к тестовой базе данных
c = db.cursor()  # создаем курсор для базы данных
test_bucket_name = 'testbucket'  # Название тестовой корзины
count_files = 3


class TestCaseCreateNewDB(unittest.TestCase):
    """
    Класс удаляет старые записи из тестовой бд, если они там имеются
    """

    def test_create(self):
        try:
            client.remove_bucket(test_bucket_name)  # удаляем корзину, если она существует
        except minio.error.S3Error:
            print('Корзины нет')
        c.execute("""DROP TABLE IF EXISTS inbox""")  # удаляем таблицу inbox, если существует
        db.commit()
        c.execute("""DROP TABLE IF EXISTS requests""")  # удаляем таблицу reqursts, если существует
        db.commit()
        # создаем новые таблицы базы данных
        c.execute("""CREATE TABLE requests
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      bucket TEXT)""")
        db.commit()
        c.execute("""CREATE TABLE inbox(id INTEGER PRIMARY KEY AUTOINCREMENT,
                     req INTEGER, filename TEXT, date_reg TEXT,
                     FOREIGN KEY(req) REFERENCES requests(id) ON DELETE CASCADE)""")
        db.commit()


class TestCaseMethods(unittest.TestCase):
    """
    Тестирование основных функций
    """

    def test_1_date_for_bucket_name(self):
        """
        Проверка названия корректного названия корзины
        """
        today = datetime.today()
        today_str = f'{today.year}{today.month:02}{today.day}'
        check_def = methods.get_bucket_name()
        self.assertEqual(check_def, today_str)

    def test_2_create_bucket(self):
        """
        Проверка создания корзины
        """
        methods.create_bucket(test_bucket_name)
        self.assertTrue(client.bucket_exists(test_bucket_name))

    def test_3_check_file_no_image(self):
        """
        Проверка файла не подходящего по условиям
        """
        files = []
        file = UploadFile('test.pdf')
        file.content_type = 'application/pdf'
        files.append(file)
        with self.assertRaises(HTTPException) as context:
            methods.check_files(files)
        self.assertEqual(400, context.exception.status_code)

    def test_4_check_file_image(self):
        """
        Проверка файла подходящего по условиям
        """
        files = []
        file = UploadFile('test.jpg')
        file.content_type = 'image/jpeg'
        files.append(file)
        self.assertEqual(None, methods.check_files(files))

    def test_5_number_of_file(self):
        """
        Проверка файлов на допустимое количество
        """
        files = []
        for i in range(16):
            file = UploadFile(f'{i}.jpg')
            file.content_type = 'image/jpeg'
            files.append(file)
        with self.assertRaises(HTTPException) as context:
            methods.check_files(files)
        self.assertEqual(400, context.exception.status_code)

    def test_6_write_to_db_req(self):
        """
        Создание записи в таблице requests
        """
        # создаем запись в таблице requests с названием тестовой корзины
        db_methods.db_requests(test_bucket_name, c, db)
        number_request = db_methods.get_db_requests(c, db)
        self.assertEqual(1, number_request)

    def test_7_add_files(self):
        """
        Проверка записи файлов в корзину min.io
        """
        files = []
        list_name_files = []  # список сгенерированных файлов
        for i in range(count_files):
            file = UploadFile(f'test_file_{i}.jpg')
            file.content_type = 'image/jpeg'
            files.append(file)
        for file in files:
            file_name = file.filename
            list_name_files.append(file_name)
            methods.add_files(file_name, file.file.read(), test_bucket_name)
            db_methods.write_to_db(file_name, c, db)
        # Получаем список файлов из корзины min.io и преобразуем в список названий файлов
        list_objects = client.list_objects(test_bucket_name)
        list_from_minio = [obj.object_name for obj in list_objects]
        self.assertEqual(list_from_minio, list_name_files)

    def test_8_get_files_from_db(self):
        """
        Проверка записи файлов в таблицу inbox
        """
        # Получаем список файлов из таблицы inbox
        list_file_from_inbox = db_methods.get_file_from_db(1, c, db)
        self.assertEqual(count_files, len(list_file_from_inbox))

    def test_9_delete_file_bucket(self):
        """
        Удаление файлов из корзины
        """
        files_list = db_methods.get_file_from_db(1, c, db)
        methods.delete_files_from_bucket(files_list, client)
        # Пытаемся получить количество файлов в тестовой корзине, должно быть равно 0
        list_objects = client.list_objects(test_bucket_name)
        list_from_minio = [obj.object_name for obj in list_objects]
        self.assertEqual(0, len(list_from_minio))

    def test_10_delete_req_from_db(self):
        """
        Удаление записей из таблицы
        """
        db_methods.delete_req_from_db(1, c, db)
        # Через SQL запрос, проверяем наличие записей в БД
        c.execute("""SELECT * FROM inbox join requests
                     on inbox.req=requests.id
                     WHERE req LIKE (?)""", (1,))
        items = c.fetchall()
        self.assertEqual(0, len(items))

    def test_after_all(self):
        """
        Удаление файлов и тестовой корзины
        """
        list_objects = client.list_objects(test_bucket_name)
        list_from_minio = [obj.object_name for obj in list_objects]
        for file in list_from_minio:
            client.remove_object(test_bucket_name, file)
        client.remove_bucket(test_bucket_name)


