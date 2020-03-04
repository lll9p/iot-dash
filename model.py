import psycopg2
import contextlib
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, Numeric
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://pi@localhost/sensor')
Base = declarative_base()
class SensorData(Base):
    __tablename__ = 'records'
    time = Column(DateTime, primary_key=True)
    temperature = Column(Numeric)
    humidity = Column(Numeric)
    def __repr__(self):
        return f"Time={self.time}\nTemperature={self.temperature}\nHumidity={self.humidity}"

class Sensor():
	def __init__(self):
	    self.Session = sessionmaker(bind=engine)
	    @contextlib.contextmanager
	    def get_session(self):
		session = self.Session()
		try:
		    yield session
		    session.commit()
		except Exception as e:
		    session.rollback()
		    raise e
		finally:
		    session.close()

