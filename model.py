import contextlib
import datetime
from collections import namedtuple

import sqlalchemy
from sqlalchemy import Column, DateTime, Numeric, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import psutil
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


class NASState():
    def __init__(self):
        self.memory = None
        self.swap = None
        self.partitions = None
        self.cpu = None
        self.loads = None
        # (0.19, 0.2, 0.17)
        # 1min 5min 15min

    def bytes2MiB(self, size):
        return size / 1048576

    def get_cpu(self):
        Core = namedtuple("Core", ("Temperature", "Frequency", "Useage"))
        Frequency = namedtuple("Frequency", ("Current", "Min", "Max"))
        temperatures = list()
        for _ in psutil.sensors_temperatures()['coretemp']:
            if _.label.startswith('Core'):
                temperatures.append(_.current)
        cpu = list()
        for temperature, frequency, useage in zip(temperatures,
                                                  psutil.cpu_freq(percpu=True),
                                                  psutil.cpu_percent(
                                                      percpu=True)
                                                  ):
            freq = Frequency._make(frequency)
            cpu.append(Core._make((temperature, freq, useage)))
        self.cpu = cpu

    def get_loads(self):
        Loads = namedtuple(
            "Loads", ("Max", "Minutes1", "Minutes5", "Minutes15"))
        self.loads = Loads._make((psutil.cpu_count(),) + psutil.getloadavg())

    def get_memory(self):
        memory = namedtuple("Memory", ("Total", "Available"))
        memory.Total, memory.Available, *_ = psutil.virtual_memory()
        memory.Total = self.bytes2Mib(memory.Total)
        memory.Available = self.bytes2Mib(memory.Available)
        self.memory = memory

    def get_partitions(self):
        Partition = namedtuple(
            "Partition", ("MountPoint", "Total", "Free"))
        partitions = psutil.disk_partitions()
        self.partitions = list()
        for _ in partitions:
            _usage = psutil.disk_usage(_.mountpoint)
            self.partitions.append(
                Partition._make(
                    (_.mountpoint,
                     self.bytes2Mib(_usage.total),
                     self.bytes2Mib(_usage.free))
                )
            )

    def get_swap(self):
        Swap = namedtuple("Swap", ("Total", "Used"))
        self.swap = Swap._make(
            map(lambda _: self.bytes2Mib(_), psutil.swap_memory()[:2]))

    def update(self):
        self.get_cpu()
        self.get_loads()
        self.get_memory()
        self.get_partitions()
        self.get_swap()

    def __repr__(self):
        return f"""CPU:{self.cpu}
loads:{self.loads}
partitions:{self.partitions}
memory:{self.memory}
swap:{self.swap}
"""


if __name__ == '__main__':
    NAS_state = NASState()
    print(NAS_state)
