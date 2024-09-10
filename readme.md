### Реализация веб сервиса для отправки файлов в min.io через fastapi.


Отправка файлов в min.io реализована через ключ доступа указанный в файле `settings.py`

Min.io развернут с помощью docker-Compose по адресу: http://45.132.18.6:9001

Таблицы:

Inboxfiles - хранит информацию о файлах: код запроса с которым была выполнена отправка, имя файла.

Requests - хранит порядковый номер отправки и наименование корзины, куда отправлялись файлы.

GroupSends - хранит номера корзин min.io
 

