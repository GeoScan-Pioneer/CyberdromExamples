import dataclasses
import threading

from piosdk.piosdk import Pioneer
from edubot_sdk.edubot_sdk import EdubotGCS
import math
import time


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

@dataclasses.dataclass
class Point:
    x: float
    y: float


class FlightPlanner:

    @classmethod
    def create_snake_traectory(cls, start_point: Point, fin_point: Point, num_x_point: int = 2, num_y_point: int = 2):
        """
        Функция для генерации списка точек в виде змейки
        :param start_point: Point(x, y)     - стартовая точка траектории
        :param fin_point: Point(x, y)       - конечная точка траектории
        :param num_x_point: int             - количество промежуточных точек вдоль оси Х
        :param num_y_point: int             - количество промежуточных точек вдоль оси У
        :return: list[Point]                - список точек для полета по траектории
        """

        traektory = []

        dx = (fin_point.x - start_point.x) / num_x_point
        dy = (fin_point.y - start_point.y) / num_y_point

        traektory.append(start_point)
        for x_point in range(num_x_point):
            for y_point in range(num_y_point):
                last_point = traektory[-1]
                if x_point % 2 == 0:
                    y = last_point.y + dy
                else:
                    y = last_point.y - dy

                traektory.append(Point(last_point.x, y))

            last_point = traektory[-1]
            x = last_point.x + dx
            traektory.append(Point(x, last_point.y))

        return traektory

    @classmethod
    def createCircleTr(cls, point: Point, radius: float, numPoints: int):
        """

        :param point:
        :param radius:
        :param numPoints:
        :return:
        """

    @staticmethod
    def checkDist(p1, p2, dist):
        d = math.dist(p1, p2)
        return True if d <= dist else False


# tr = FlightPlanner.create_snake_traectory(Point(-4, -4), Point(4, 4), 8, 3)
tr = FlightPlanner.create_snake_traectory(Point(0, -4), Point(4, 4), 8, 2)

drone = Pioneer(ip=DroneConnectingData.drone0.ip, mavlink_port=DroneConnectingData.drone0.port)
robot = EdubotGCS(ip=RobotConnectingData.robot0.ip, mavlink_port=RobotConnectingData.robot0.port)

fire_point = [0, 0, 0]
is_new_fire = False


def search():
    """
    Функция для поиска пожаров. drone будет бесконечно летать по траектории и искать пожары
    """
    global fire_point, is_new_fire

    # Завести моторы и взлететь
    drone.arm()
    drone.takeoff()
    """ Бесконеынй поиск пожаров """
    newPoint = True
    i = 0
    pos = None

    while True:
        # если можем лететь в новую точку
        if newPoint:
            drone.go_to_local_point(tr[i].x, tr[i].y, 1)
            i += 1

            # нуление индекса точки для зацикливания траектории
            if i >= len(tr):
                i = 0

            newPoint = False

        # Если дрон достиг точки полета
        if drone.point_reached():
            newPoint = True


        p = drone.get_local_position_lps()
        if p is not None:
            pos = p

        temp = drone.get_piro_sensor_data()
        if temp is not None:
            # если температура больше 40 и находится в полуметре от последней обнаруженной точки пожара. Иначе дрон будет обнаружевать один и тот же пожар.
            if temp >= 40 and not FlightPlanner.checkDist(fire_point[:2], pos[:2], 0.5):
                # цветовая индикация пожара
                drone.fire_detection()
                fire_point = pos
                is_new_fire = True

                # остановка в текущей точке
                drone.go_to_local_point(pos[0], pos[1], 1)
                time.sleep(5)
                drone.point_reached()

                # продолджение полета по траектории
                drone.go_to_local_point(tr[i - 1].x, tr[i - 1].y, 1)

        time.sleep(0.02)


def detecting():
    """
    Функция для тушения пожарв роботом
    """
    global fire_point, is_new_fire
    while True:
        # Если есть найденный пожар
        if is_new_fire:
            is_new_fire = False

            robot.go_to_local_point(x=fire_point[0], y=fire_point[1])

        if robot.point_reached():
            # При достижении точки выполняется индикация
            robot.fire_detection()

        time.sleep(0.02)

# Запуск функций в отдельных потоках
th1 = threading.Thread(target=search)
th2 = threading.Thread(target=detecting)

th1.start()
th2.start()

while True:
    time.sleep(1)