import sqlite3
from datetime import datetime
from models import GroupSends, engine, RequestsNames, InboxFiles
from sqlalchemy.orm import Session
import itertools
from sqlalchemy import select

data_base = sqlite3.connect('files.sqlite')
cursor_db = data_base.cursor()
session = Session(bind=engine)


def add_information_about_group_send_alchemy(number_bucket: str) -> bool:
    """Запись названия корзины в таблицу GroupSends"""
    new_bucket = GroupSends(bucket_name=number_bucket)
    session.add(new_bucket)
    session.commit()
    return True


def get_bucket_info_alchemy(bucket_name: str) -> int:
    """Получение id корзины"""
    bucket = session.query(GroupSends).filter_by(bucket_name=bucket_name).one()
    print(f'bucket.id: {bucket.id}; bucket_name={bucket.bucket_name}')
    return bucket.id


def create_request_number_alchemy(bucket_id: int) -> int:
    """Создание записи об отправке в таблице RequestsNames"""
    new_request = RequestsNames(bucket_id=bucket_id)
    session.add(new_request)
    session.commit()
    return new_request.id


def create_info_about_file_to_db_alchemy(request_number: int, file_name: str) -> bool:
    """Запись информации в бд о загруженных файлах"""
    try:
        new_file = InboxFiles(file_name=file_name, send_number_id=request_number)
        session.add(new_file)
        session.commit()
        return True
    except Exception as e:
        print(e)
        return False


def get_file_list_from_db_alchemy(req_id: int) -> dict:
    """
    Получение данных о файлах по id корзины
    """
    files = session.query(InboxFiles).filter_by(send_number_id=req_id)
    bucket_id = session.query(RequestsNames).get(req_id).bucket_id
    bucket_name = session.query(GroupSends).get(bucket_id).bucket_name

    result = {'bucket_id': bucket_id,
              'bucket_name': bucket_name,
              'req_id': req_id}
    files_dict = {}
    num = itertools.count(1, 1)
    for file in files:
        files_dict[next(num)] = file.file_name
        print(file.file_name)
    result['files'] = files_dict
    return result


def delete_file_list_from_db_alchemy(req_id: int):
    """
    Удаление записей из базы данных
    """
    request_for_del = session.query(RequestsNames).get(req_id)
    session.delete(request_for_del)
    session.commit()
    try:
        session.delete(request_for_del)
        session.commit()
        return f'Файлы удалены из базы данных'
    except Exception as e:
        return e

# def db_requests(number_bucket: str, c=cursor_db, db=data_base):
#     """
#     Добавление в таблицу записи в какую корзину добавляются файлы
#     :param db: база данных
#     :param c: курсор базы данных
#     :param number_bucket: название корзины
#     :return:
#     """
#     c.execute("INSERT INTO requests (bucket) VALUES (?)", (number_bucket,))
#     db.commit()
#
#
# def get_db_requests(c=cursor_db, db=data_base) -> int:
#     """
#     Получение порядкового номера запроса
#     :param db: база данных
#     :param c: курсор базы данных
#     :return: Порядковый номер последнего запроса
#     """
#     num = (c.execute("SELECT max(id) FROM requests").fetchone()[0])
#     db.commit()
#     return num
#
#
# def write_to_db(file_name: str, c=cursor_db, db=data_base):
#     """
#     Функция записывает в базу отправленные файлы
#     :param db: база данных
#     :param c: курсор базы данных
#     :param file_name: str название файла
#     """
#     str_date = datetime.now()
#     num = c.execute("SELECT max(id) FROM requests").fetchone()[0]
#     c.execute("INSERT INTO inbox(req, filename, date_reg) VALUES (?,?,?)",
#               (num, f'{file_name}', f'{str_date.strftime("%d-%m-%Y %H:%M")}'))
#     db.commit()
#
#
# def get_file_from_db(req_number: int, c=cursor_db, db=data_base) -> list:
#     """
#     Функция по номеру запроса формирует sql запрос и возвращает перечень файлов.
#     :param req_number: номер запроса
#     :param db: база данных
#     :param c: курсор базы данных
#     :return: список кортежей с информацией о файлах
#     """
#     c.execute("""SELECT filename, date_reg, bucket FROM inbox join requests
#                  on inbox.req=requests.id
#                  WHERE req LIKE (?)""", (req_number,))
#     items = c.fetchall()
#     db.commit()
#     return items
#
#
# def get_name_bucket_from_db(req_number: int, c=cursor_db, db=data_base):
#     c.execute("""SELECT bucket FROM requests
#                  WHERE id LIKE (?)""", (req_number,))
#     item = c.fetchall()
#     return item
#
#
# def delete_req_from_db(req_number: int, c=cursor_db, db=data_base):
#     """
#     Функция удаляет записи из таблицы
#     :param req_number: номер запроса
#     :param db: база данных
#     :param c: курсор базы данных
#     """
#     c.execute("""PRAGMA foreign_keys = ON""")
#     c.execute("""DELETE FROM requests
#                  WHERE id = (?)""", (req_number,))
#     db.commit()
