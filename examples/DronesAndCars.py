import dataclasses
import time
from threading import Thread

from edubot_sdk.edubot_sdk import EdubotGCS  # Импортируем класс РТС
from piosdk.piosdk import Pioneer  # Импортируем класс Pioneer


# Классы для хранения настроек подключения
@dataclasses.dataclass
class IpPort:
    ip: str
    port: int


class DroneConnectingData:
    drone0: IpPort = IpPort(ip="127.0.0.1", port=8000)
    drone1: IpPort = IpPort(ip="127.0.0.1", port=8001)
    drone2: IpPort = IpPort(ip="127.0.0.1", port=8002)
    drone3: IpPort = IpPort(ip="127.0.0.1", port=8003)


class RobotConnectingData:
    robot0: IpPort = IpPort(ip="127.0.0.1", port=8004)
    robot1: IpPort = IpPort(ip="127.0.0.1", port=8005)
    robot2: IpPort = IpPort(ip="127.0.0.1", port=8006)
    robot3: IpPort = IpPort(ip="127.0.0.1", port=8007)


# код программы...

# Создание дронов и роботов
p_1 = Pioneer(ip=DroneConnectingData.drone0.ip, mavlink_port=DroneConnectingData.drone0.port)
p_2 = Pioneer(ip=DroneConnectingData.drone1.ip, mavlink_port=DroneConnectingData.drone1.port)

e_1 = EdubotGCS(ip=RobotConnectingData.robot0.ip, mavlink_port=RobotConnectingData.robot0.port)
e_2 = EdubotGCS(ip=RobotConnectingData.robot1.ip, mavlink_port=RobotConnectingData.robot1.port)
e_3 = EdubotGCS(ip=RobotConnectingData.robot2.ip, mavlink_port=RobotConnectingData.robot2.port)

# отпрвка первогооробота в точку 5 5
e_1.go_to_local_point(5, 5)

while True:
    # Если робот 1 доссиг точки, то отправка роботов 2 и 3 в точки
    if e_1.point_reached():
        Thread(target=e_2.go_to_local_point, args=[3, 1]).start()
        Thread(target=e_3.go_to_local_point, args=[2.3, 4]).start()

    # Если робот 2 достиг точки
    if e_2.point_reached():
        # взлет, цветовая индикация и полет в точку
        p_1.arm()
        p_1.takeoff()
        p_1.led_custom(mode=2, timer=10, color1=[127, 12, 41], color2=[55, 171, 42])
        p_1.go_to_local_point(-4, -4.9, 1.5)

    # получение температуры с первого дрона
    data = p_1.get_piro_sensor_data(blocking=True)
    if data:
        pos = p_1.get_local_position_lps(blocking=True)
        if pos:
            print(data, pos)

    # Если дрон 1 достиг точки
    if p_1.point_reached():
        # посадка, взлет, полет в тчоку и цветовая индикация
        p_1.land()
        p_2.arm()
        p_2.takeoff()
        p_2.go_to_local_point(4.0, 0, 1.5)
        p_2.led_control(r=200, g=124, b=12)

    data = p_2.get_qr_reader_data(blocking=True)
    if data:
        pos = p_2.get_local_position_lps(blocking=True)
        if pos:
            print(data, pos)

    if p_2.point_reached():
        p_2.land()
        p_2.led_control(r=189, g=34, b=11)

    time.sleep(0.01)
