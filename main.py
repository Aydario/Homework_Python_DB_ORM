import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
from models import create_tables, Publisher, Book, Sale, Shop, Stock
from dotenv import load_dotenv
import os
import json

# Загрузка переменных окружения из .env файла
load_dotenv()


# Функция для вставки данных из JSON-файла в БД
def enter_data(json_file: str, session: sql.orm.Session) -> None:
    """
    Вставляет данные из JSON-файла в БД.

    :param json_file: JSON-файл с данными.
    :param session: Сессия  для выполнения операций с БД.
    """
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

        for model in data:
            if model['model'] == 'publisher':
                session.add(Publisher(name=model['fields']['name']))
            elif model['model'] == 'book':
                session.add(Book(title=model['fields']['title'],
                                 id_publisher=model['fields']['id_publisher']))
            elif model['model'] == 'shop':
                session.add(Shop(name=model['fields']['name']))
            elif model['model'] == 'stock':
                session.add(Stock(id_shop=model['fields']['id_shop'],
                                  id_book=model['fields']['id_book'],
                                  count=model['fields']['count']))
            elif model['model'] == 'sale':
                session.add(Sale(price=model['fields']['price'],
                                 date_sale=model['fields']['date_sale'],
                                 count=model['fields']['count'],
                                 id_stock=model['fields']['id_stock']))

    session.commit()


# Функция для отбора покупок книг издателя
def select_sales(publisher_name_or_id: str, session: sql.orm.Session) -> sql.orm.Query:
    """
    Отбирает покупки книг издателя.

    :param publisher_name_or_id: Имя или идентификатор издателя.
    :param session: Сессия для выполнения операций с БД.
    :return: Запрос к БД с покупками книг издателя.
    """
    if publisher_name_or_id.isdigit():
        publisher = session.query(Publisher).filter_by(id=int(publisher_name_or_id)).first()
    else:
        publisher = session.query(Publisher).filter(
            sql.func.lower(Publisher.name) == publisher_name_or_id.lower()).first()
    if not publisher:
        return

    sales = session.query(Sale, Book, Shop).join(Stock, Sale.id_stock == Stock.id).join(
        Book, Stock.id_book == Book.id).join(Shop, Stock.id_shop == Shop.id).join(
        Publisher, Book.id_publisher == Publisher.id).filter(Publisher.id == publisher.id or
                                                             Publisher.name == publisher.name)

    return sales


# Загрузка переменных окружения
database = os.getenv("database")
user = os.getenv("user")
password = os.getenv("password")

# Создание строки подключения к БД
DSN = f'postgresql://{user}:{password}@localhost:5432/{database}'
engine = sql.create_engine(DSN)

# Создание таблиц в БД
create_tables(engine)

# Создание сессии
Session = sessionmaker(bind=engine)
session = Session()

# Вставка данных из JSON-файла в БД
enter_data('tests_data.json', session)

# Ввод имени или идентификатора издателя
publisher_name_or_id = input('Введите имя или идентификатор издателя:-> ')

# Отбор покупок книг издателя
sales = select_sales(publisher_name_or_id, session)
if sales:
    # Определение максимальных длин для выравнивания вывода
    max_book_title_length = max(len(book.title) for sale, book, shop in sales)
    max_shop_name_length = max(len(shop.name) for sale, book, shop in sales)
    max_sale_price_length = max(len(str(sale.price)) for sale, book, shop in sales)
    for sale, book, shop in sales:
        print(f"{book.title:<{max_book_title_length}} | {shop.name:<{max_shop_name_length}} | "
              f"{sale.price:<{max_sale_price_length}} | {sale.date_sale}")

else:
    print('Издатель не найден')

# Закрытие сессии
session.close()
