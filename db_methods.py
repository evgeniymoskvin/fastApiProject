import itertools
import logging

from sqlalchemy import select

from models import GroupSends, InboxFiles, RequestsNames, engine, engine_async
from sqlalchemy.orm import Session
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

session = Session(bind=engine)
session_async = AsyncSession(bind=engine_async)
logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w")


async def add_information_about_group_send_alchemy(number_bucket: str) -> bool:
    """Запись названия корзины в таблицу GroupSends"""
    new_bucket = GroupSends(bucket_name=number_bucket)
    session_async.add(new_bucket)
    await session_async.commit()
    return True


async def get_bucket_info_alchemy(bucket_name: str) -> int:
    """Получение id корзины по наименованию"""
    stmt = select(GroupSends).where(GroupSends.bucket_name == bucket_name)
    result: Result = await session_async.execute(stmt)
    bucket = result.scalar_one_or_none()
    # bucket = session.query(GroupSends).filter_by(bucket_name=bucket_name).one()
    logging.info(
        f"{get_bucket_info_alchemy.__name__} - bucket.id: {bucket.id}; bucket_name={bucket.bucket_name}"
    )
    return bucket.id


async def create_request_number_alchemy(bucket_id: int) -> int:
    """Создание записи об отправке в таблице RequestsNames"""
    new_request = RequestsNames(bucket_id=bucket_id)
    session_async.add(new_request)
    await session_async.commit()
    await session_async.refresh(new_request, attribute_names=["id"])
    logging.info(
        f"{create_request_number_alchemy.__name__} - RequestsNames create: {new_request.id}"
    )
    return new_request.id


async def create_info_about_file_to_db_alchemy(
    request_number: int, file_name: str
) -> bool:
    """Запись информации в бд о загруженных файлах"""
    try:
        new_file = InboxFiles(file_name=file_name, send_number_id=request_number)
        session_async.add(new_file)
        await session_async.commit()
        return True
    except Exception as e:
        logging.error(f"{create_info_about_file_to_db_alchemy.__name__} - {e}")
        return False


async def get_file_list_from_db_alchemy(req_id: int) -> dict:
    """
    Получение данных о файлах по id корзины
    """
    stmt_files = select(InboxFiles).where(InboxFiles.send_number_id == req_id)
    result_files: Result = await session_async.execute(stmt_files)
    files = result_files.scalars()

    stmt_req = select(RequestsNames).where(RequestsNames.id == req_id)
    result_req: Result = await session_async.execute(stmt_req)
    bucket_id = result_req.scalar_one_or_none().bucket_id

    stmt_bucket = select(GroupSends).where(GroupSends.id == bucket_id)
    result_bucket: Result = await session_async.execute(stmt_bucket)
    bucket_name = result_bucket.scalar_one_or_none().bucket_name

    result = {"bucket_id": bucket_id, "bucket_name": bucket_name, "req_id": req_id}
    files_dict = {}
    num = itertools.count(1, 1)
    for file in files:
        files_dict[next(num)] = file.file_name
    result["files"] = files_dict
    return result


async def delete_file_list_from_db_alchemy(req_id: int):
    """
    Удаление записей из базы данных
    """
    stmt = select(RequestsNames).where(RequestsNames.id == req_id)
    result: Result = await session_async.execute(stmt)
    request_for_del = result.scalar_one_or_none()
    try:
        await session_async.delete(request_for_del)
        await session_async.commit()
        return "Файлы удалены из базы данных"
    except Exception as e:
        logging.error(f"{delete_file_list_from_db_alchemy.__name__} - {e}")
        return e
