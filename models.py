import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

# Создание базового класса для моделей
Base = declarative_base()


# Определение модели Publisher
class Publisher(Base):
    """
    Модель для таблицы publisher.

    Атрибуты:
    - id: Идентификатор издателя (первичный ключ).
    - name: Название издателя (уникальное, не может быть пустым).
    """
    __tablename__ = 'publisher'

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=50), unique=True, nullable=False)

    # Отношение один-ко-многим с таблицей Book
    # Publisher.books связывает издателя с его книгами
    books = relationship("Book", backref="publisher")


# Определение модели Book
class Book(Base):
    """
    Модель для таблицы book.

    Атрибуты:
    - id: Идентификатор книги (первичный ключ).
    - title: Название книги (не может быть пустым).
    - id_publisher: Идентификатор издателя (внешний ключ).
    """
    __tablename__ = 'book'

    id = sq.Column(sq.Integer, primary_key=True)
    title = sq.Column(sq.String(length=100), nullable=False)
    id_publisher = sq.Column(sq.Integer, sq.ForeignKey('publisher.id'))

    # Отношение один-ко-многим с таблицей Stock
    # Book.stocks связывает книгу со складом
    stocks = relationship("Stock", backref="book")


# Определение модели Shop
class Shop(Base):
    """
    Модель для таблицы магазинов.

    Атрибуты:
    - id: Идентификатор магазина (первичный ключ).
    - name: Название магазина (не может быть пустым).
    """
    __tablename__ = 'shop'

    id = sq.Column(sq.Integer, primary_key=True)
    name = sq.Column(sq.String(length=50), nullable=False)

    # Отношение один-ко-многим с таблицей Stock
    # Shop.stocks связывает магазин со складом
    stocks = relationship("Stock", backref="shop")


# Определение модели Stock
class Stock(Base):
    """
    Модель для таблицы записей на складе.

    Атрибуты:
    - id: Идентификатор записи на складе (первичный ключ).
    - id_book: Идентификатор книги (внешний ключ).
    - id_shop: Идентификатор магазина (внешний ключ).
    - count: Количество книг на складе (не может быть пустым).
    """
    __tablename__ = 'stock'

    id = sq.Column(sq.Integer, primary_key=True)
    id_book = sq.Column(sq.Integer, sq.ForeignKey('book.id'))
    id_shop = sq.Column(sq.Integer, sq.ForeignKey('shop.id'))
    count = sq.Column(sq.Integer, nullable=False)

    # Отношение один-ко-многим с таблицей Sale
    # Stock.sales связывает запись на складе с её продажами
    sales = relationship("Sale", backref="stock")


# Определение модели Sale
class Sale(Base):
    """
    Модель для таблицы продаж.

    Атрибуты:
    - id: Идентификатор продажи (первичный ключ).
    - price: Цена продажи (не может быть пустым).
    - date_sale: Дата продажи (не может быть пустым).
    - id_stock: Идентификатор записи на складе (внешний ключ).
    - count: Количество проданных книг (не может быть пустым).
    """
    __tablename__ = 'sale'

    id = sq.Column(sq.Integer, primary_key=True)
    price = sq.Column(sq.Float, nullable=False)
    date_sale = sq.Column(sq.Date, nullable=False)
    id_stock = sq.Column(sq.Integer, sq.ForeignKey('stock.id'))
    count = sq.Column(sq.Integer, nullable=False)


# Функция для создания таблиц в БД
def create_tables(engine: sq.engine.Engine) -> None:
    """
    Создает таблицы в базе данных.

    :param engine: Движок для подключения к БД.
    """
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
