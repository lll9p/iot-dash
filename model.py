import contextlib
import datetime
from collections import namedtuple
from itertools import islice

import psutil
import sqlalchemy
from sqlalchemy import Column, DateTime, Float, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import db_host, db_name, db_password, db_user


def window(seq, n=2):
    "Returns a sliding window (of width n) over data from the iterable"
    "   s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...                   "
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result


class Sensor():
    def __init__(self):
        engine = create_engine(
            f'postgresql://{db_user}:{db_password}@{db_host}/{db_name}')
        self.Session = sessionmaker(bind=engine)
        self.session = self.create_session()
        self.model = self.create_model()
        self.filter_on = True

    def create_model(self):
        Base = declarative_base()

        class SensorModel(Base):
            __tablename__ = 'records'
            time = Column(DateTime, primary_key=True)
            temperature = Column(Float)
            humidity = Column(Float)

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

    def get_data_by_time(self: type, start_date: str, end_date: str) \
            -> sqlalchemy.orm.query.Query:
        data = None
        today_ = datetime.date.today()
        start_date_ = datetime.date.fromisoformat(start_date)
        end_date_ = datetime.date.fromisoformat(end_date)
        if start_date_ >= end_date_:
            start_date = str(
                end_date_ - datetime.timedelta(days=1))
        if end_date_ == today_:
            # not just monitor from today 00:00
            end_date = str(today_ + datetime.timedelta(days=1))
        if (start_date_ > today_) or (end_date_ >
                                      today_ + datetime.timedelta(days=1)):
            start_date = str(today_)
            end_date = str(today_ - datetime.timedelta(days=1))
        with self.session() as session:
            data = session.query(
                self.model).filter(
                self.model.time.between(start_date, end_date),)
        return self.transpose(data)

    def transpose(self: type, data: sqlalchemy.orm.query.Query) -> \
            [datetime.datetime, float, float]:
        data = data.all()
        if self.filter_on:
            len_data = len(data)
            for i in range(0, len_data, 3):
                if len_data - i < 3:
                    break
                max_ = data[i] if data[i].temperature > \
                    data[i +
                         1].temperature else data[i + 1]
                max_ = max_ if max_.temperature > \
                    data[i +
                         2].temperature else data[i + 2]
                min_ = data[i] if data[i].temperature < \
                    data[i +
                         1].temperature else data[i + 1]
                min_ = min_ if min_.temperature < \
                    data[i +
                         2].temperature else data[i + 2]
                if abs(max_.temperature - min_.temperature) > 9.0:
                    mean = sum(_.temperature for _ in data[i:i + 3]) / 3
                    if abs(max_.temperature -
                           mean) > abs(min_.temperature - mean):
                        max_.time = None
                    else:
                        min_.time = None
                max_ = data[i] if data[i].humidity > \
                    data[i +
                         1].humidity else data[i + 1]
                max_ = max_ if max_.humidity > \
                    data[i +
                         2].humidity else data[i + 2]
                min_ = data[i] if data[i].humidity < \
                    data[i +
                         1].humidity else data[i + 1]
                min_ = min_ if min_.humidity < \
                    data[i +
                         2].humidity else data[i + 2]
                if abs(max_.humidity - min_.humidity) > 13.0:
                    mean = sum(_.humidity for _ in data[i:i + 3]) / 3
                    if abs(max_.humidity - mean) > abs(min_.humidity - mean):
                        max_.time = None
                    else:
                        min_.time = None
            data = filter(lambda _: _.time, data)
        result = zip(*((model.time, model.temperature, model.humidity)
                       for model in data))
        return result

    def statistics(self, data):
        # find 2 point difference absolute
        # temperature diff should <=9.3
        # humidity diff should <= 13.0
        data = list(data)
        point_diff1 = list(abs(i - j) for i, j in window(data[1]))
        point_diff2 = list(abs(i - j) for i, j in window(data[2]))
        with open('point_diff1', mode='w') as file:
            file.write(str(point_diff1))
        with open('point_diff2', mode='w') as file:
            file.write(str(point_diff2))


class NASState():
    def __init__(self):
        self.memory = None
        self.swap = None
        self.partitions = None
        self.cpu = None
        self.loads = None
        self.update()
        # (0.19, 0.2, 0.17)
        # 1min 5min 15min

    def bytes2MiB(self, size):
        return size / 1048576

    def get_cpu(self):
        Core = namedtuple("Core", ("Temperature", "Frequency", "Useage"))
        Frequency = namedtuple("Frequency", ("Current", "Min", "Max"))
        if not psutil.WINDOWS:
            # Function sensors_temperatures is not available on Windows.
            temperatures = list()
            for _ in psutil.sensors_temperatures()['coretemp']:
                if _.label.startswith('Core'):
                    temperatures.append(_.current)
        else:
            temperatures = [-1] * psutil.cpu_count()
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
        memory.Total = self.bytes2MiB(memory.Total)
        memory.Available = self.bytes2MiB(memory.Available)
        self.memory = memory

    def get_partitions(self):
        Partition = namedtuple(
            "Partition", ("Device", "MountPoint", "Total", "Free"))
        partitions = psutil.disk_partitions()
        self.partitions = list()
        for _ in partitions:
            _usage = psutil.disk_usage(_.mountpoint)
            self.partitions.append(
                Partition._make(
                    (_.device,
                     _.mountpoint,
                     self.bytes2MiB(_usage.total),
                     self.bytes2MiB(_usage.free))
                )
            )
        self.partitions.sort(key=lambda _: _[0])

    def get_swap(self):
        Swap = namedtuple("Swap", ("Total", "Used"))
        self.swap = Swap._make(
            map(lambda _: self.bytes2MiB(_), psutil.swap_memory()[:2]))

    def update(self):
        self.get_cpu()
        self.get_loads()
        self.get_memory()
        self.get_partitions()
        self.get_swap()

    def __repr__(self):
        result = f"""### Loads
| 1Min | 5Min | 15Min |
| :----: | :----: | :-----: |
| {self.loads.Minutes1:.1f} | """ + \
            f"{self.loads.Minutes5:>.1f} | {self.loads.Minutes15:.1f} |\n" + \
            f"""### CPU
| Core | Temperature(℃) | Frequency(MHz) | Usage(%) |
| :--: | :--: | :--: | :--: |
"""
        for index, core in enumerate(self.cpu):
            result += f"| {index} " + \
                f"| {core.Temperature:.1f} " + \
                f"| {core.Frequency.Current:.1f} " + \
                f"| {core.Useage:>10.1f} |\n"
        result += '\n'
        result += f"""### Partitions
| Device | MountPoint | Total(MiB) | Free(MiB) | Usage(%) |
| :----: | :--------: | :--------: | :-------: | :------: |
"""
        for partition in self.partitions:
            usage = 100 * (partition.Total - partition.Free) \
                / partition.Total
            result += f"| {partition.Device} " + \
                f"| {partition.MountPoint} " + \
                f"| {partition.Total:.1f} " + \
                f"| {partition.Free:.1f} " + \
                f"| {usage:.1f} |\n"
        result += '\n'
        result += f"""### Memory
| Total(MiB) | Available(MiB) | Available(%) |
| :--------: | :------------: | :----------: |
"""
        result += f"| {self.memory.Total:.1f} " + \
            f"| {self.memory.Available:.1f} " + \
            f"| {(self.memory.Available*100/self.memory.Total):.1f} |\n"
        result += '\n'
        result += f"""### Swap
| Total(MiB) | Available(MiB) | Available(%) |
| :--------: | :------------: | :----------: |
"""
        swap_avail = (self.swap.Total - self.swap.Used) * 100 / \
            self.swap.Total if self.swap.Total > 0 else 0
        result += f"| {self.swap.Total:.1f} " + \
            f"| {(self.swap.Total-self.swap.Used):.1f} " + \
            f"| {swap_avail:.1f} |\n"
        return result


if __name__ == '__main__':
    sensor = Sensor()
    list(sensor.get_data_by_time("2019-05-01", "2020-03-06"))
