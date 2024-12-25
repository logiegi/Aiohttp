from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from settings import DSN

engine = create_async_engine(DSN, pool_pre_ping=True)

from sqlalchemy.orm import declarative_base, sessionmaker

Session = sessionmaker(bind=engine,
                       class_=AsyncSession,
                       expire_on_commit=False,
                       )
Base = declarative_base()

from sqlalchemy import Column, Integer, String, DateTime, func


# модель пользователя:
class User(Base):
    __tablename__ = 'ad_users'  # имя таблицы прописывается явно

    # колонки не создаются по умолчанию, как в Джанго - здесь сами делаем:

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    username = Column(
        String,
        nullable=False,
        unique=True,
        index=True
    )
    password = Column(
        String,
        nullable=False
    )
    email = Column(
        String,
        nullable=False,
        index=True
    )
    reg_time = Column(
        DateTime,
        server_default=func.now()
    )  # вызовет в postgres
    # метод now() - текущее время
    # postgres сам проставит время !!!

    def info_dict(self):
        info = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            "reg_time": int(self.reg_time.timestamp())
            }
        return info

    def __str__(self):
        return f'Ads user: {self.info_dict()}'


# модель объявления:
class Ad(Base):
    __tablename__ = 'ads'

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )
    header = Column(
        String,
        nullable=False,
        index=True
    )
    description = Column(
        String
    )
    creation_time = Column(
        DateTime,
        server_default=func.now()
    )
    user_id = Column(
        Integer,
        nullable=False
    )

    def info_dict(self):
        info = {
            'id': self.id,
            'header': self.name,
            'description': self.description,
            'user_id': self.email,
            'creation_time': int(self.creation_time.timestamp())
            }
        return info

    def __str__(self):
        return f'Ad project: {self.info_dict()}'