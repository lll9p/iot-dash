import cProfile
from model import Sensor
sensor = Sensor()

cProfile.run('list(sensor.get_data_by_time("2019-05-01", "2020-03-06"))')

