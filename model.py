import contextlib
import datetime

import sqlalchemy
from sqlalchemy import Column, DateTime, Numeric, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import db_host, db_name, db_password, db_user


class Sensor():
    def __init__(self):
        engine = create_engine(
            f'postgresql://{db_user}:{db_password}@{db_host}/{db_name}')
        self.Session = sessionmaker(bind=engine)
        self.session = self.create_session()
        self.model = self.create_model()

    def create_model(self):
        Base = declarative_base()

        class SensorModel(Base):
            __tablename__ = 'records'
            time = Column(DateTime, primary_key=True)
            temperature = Column(Numeric)
            humidity = Column(Numeric)

            def __repr__(self):
                return f"""Time={self.time}
Temperature={self.temperature}
Humidity={self.humidity}"""
        return SensorModel

    def create_session(self):
        @contextlib.contextmanager
        def get_session():
            session = self.Session()
            try:
                yield session
                session.commit()
            except Exception as e:
                session.rollback()
                raise e
            finally:
                session.close()
        return get_session

    def get_data_by_time(self: type, time_after: str) \
            -> sqlalchemy.orm.query.Query:
        data = None
        with self.session() as session:
            data = session.query(
                self.model).filter(
                self.model.time > time_after)
        return self.transpose(data)

    def transpose(self: type, data: sqlalchemy.orm.query.Query) \
            -> [datetime.datetime, float, float]:
        result = zip(*((model.time, model.temperature, model.humidity)
                       for model in data.all()))
        return result
