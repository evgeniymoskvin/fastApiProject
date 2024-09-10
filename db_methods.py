import itertools
import logging

from models import GroupSends, InboxFiles, RequestsNames, engine
from sqlalchemy.orm import Session

session = Session(bind=engine)
logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w")


def add_information_about_group_send_alchemy(number_bucket: str) -> bool:
    """Запись названия корзины в таблицу GroupSends"""
    new_bucket = GroupSends(bucket_name=number_bucket)
    session.add(new_bucket)
    session.commit()
    return True


def get_bucket_info_alchemy(bucket_name: str) -> int:
    """Получение id корзины по наименованию"""
    bucket = session.query(GroupSends).filter_by(bucket_name=bucket_name).one()
    logging.info(
        f"{get_bucket_info_alchemy.__name__} - bucket.id: {bucket.id}; bucket_name={bucket.bucket_name}"
    )
    return bucket.id


def create_request_number_alchemy(bucket_id: int) -> int:
    """Создание записи об отправке в таблице RequestsNames"""
    new_request = RequestsNames(bucket_id=bucket_id)
    session.add(new_request)
    session.commit()
    logging.info(
        f"{create_request_number_alchemy.__name__} - RequestsNames create: {new_request.id}"
    )
    return new_request.id


def create_info_about_file_to_db_alchemy(request_number: int, file_name: str) -> bool:
    """Запись информации в бд о загруженных файлах"""
    try:
        new_file = InboxFiles(file_name=file_name, send_number_id=request_number)
        session.add(new_file)
        session.commit()
        return True
    except Exception as e:
        logging.error(f"{create_info_about_file_to_db_alchemy.__name__} - {e}")
        return False


def get_file_list_from_db_alchemy(req_id: int) -> dict:
    """
    Получение данных о файлах по id корзины
    """
    files = session.query(InboxFiles).filter_by(send_number_id=req_id)
    bucket_id = session.query(RequestsNames).get(req_id).bucket_id
    bucket_name = session.query(GroupSends).get(bucket_id).bucket_name
    result = {"bucket_id": bucket_id, "bucket_name": bucket_name, "req_id": req_id}
    files_dict = {}
    num = itertools.count(1, 1)
    for file in files:
        files_dict[next(num)] = file.file_name
    result["files"] = files_dict
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
        return "Файлы удалены из базы данных"
    except Exception as e:
        logging.error(f"{delete_file_list_from_db_alchemy.__name__} - {e}")
        return e
