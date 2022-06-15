import sqlite3
from datetime import datetime

data_base = sqlite3.connect('greenatom.sqlite')
cursor_db = data_base.cursor()


def db_requests(number_bucket: str, c=cursor_db, db=data_base):
    """
    Добавление в таблицу записи в какую корзину добавляются файлы
    :param db: база данных
    :param c: курсор базы данных
    :param number_bucket: название корзины
    :return:
    """
    c.execute("INSERT INTO requests (bucket) VALUES (?)", (number_bucket,))
    db.commit()


def get_db_requests(c=cursor_db, db=data_base) -> int:
    """
    Получение порядкового номера запроса
    :param db: база данных
    :param c: курсор базы данных
    :return: Порядковый номер последнего запроса
    """
    num = (c.execute("SELECT max(id) FROM requests").fetchone()[0])
    db.commit()
    return num


def write_to_db(file_name: str, c=cursor_db, db=data_base):
    """
    Функция записывает в базу отправленные файлы
    :param db: база данных
    :param c: курсор базы данных
    :param file_name: str название файла
    """
    str_date = datetime.now()
    num = c.execute("SELECT max(id) FROM requests").fetchone()[0]
    c.execute("INSERT INTO inbox(req, filename, date_reg) VALUES (?,?,?)",
              (num, f'{file_name}', f'{str_date.strftime("%d-%m-%Y %H:%M")}'))
    db.commit()


def get_file_from_db(req_number: int, c=cursor_db, db=data_base) -> list:
    """
    Функция по номеру запроса формирует sql запрос и возвращает перечень файлов.
    :param req_number: номер запроса
    :param db: база данных
    :param c: курсор базы данных
    :return: список кортежей с информацией о файлах
    """
    c.execute("""SELECT filename, date_reg, bucket FROM inbox join requests
                 on inbox.req=requests.id
                 WHERE req LIKE (?)""", (req_number,))
    items = c.fetchall()
    db.commit()
    return items


def delete_req_from_db(req_number: int, c=cursor_db, db=data_base):
    """
    Функция удаляет записи из таблицы
    :param req_number: номер запроса
    :param db: база данных
    :param c: курсор базы данных
    """
    c.execute("""PRAGMA foreign_keys = ON""")
    c.execute("""DELETE FROM requests
                 WHERE id = (?)""", (req_number,))
    db.commit()
