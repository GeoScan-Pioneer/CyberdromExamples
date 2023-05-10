import dataclasses

from piosdk.piosdk import Pioneer


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


drones = []
drones.append(Pioneer(ip=DroneConnectingData.drone0.ip, mavlink_port=DroneConnectingData.drone0.port))
drones.append(Pioneer(ip=DroneConnectingData.drone1.ip, mavlink_port=DroneConnectingData.drone1.port))
drones.append(Pioneer(ip=DroneConnectingData.drone2.ip, mavlink_port=DroneConnectingData.drone2.port))
drones.append(Pioneer(ip=DroneConnectingData.drone3.ip, mavlink_port=DroneConnectingData.drone3.port))

# Словарь с точками
position_object = {
    "home_drone":
        {
            'drone0': [1, 1.5, 1],
            'drone1': [1, 2.5, 1],
            'drone2': [1, 3.5, 1],
            'drone3': [1, 4.5, 1]
        },
    "points_interest":
        {
            "point0": [-3.5, 1.5, 1],
            "point1": [-3.5, 4, 1],
            "point2": [-1, 2.5, 1],
            "point3": [-1, 2, 1]
        }
}

# Создание массива с точками, взятыми из словаря выше
mission_for_drone = [
    [
        position_object["points_interest"]["point0"],
        position_object["home_drone"]["drone0"]
    ],
    [
        position_object["points_interest"]["point1"],
        position_object["home_drone"]["drone1"]
    ],
    [
        position_object["points_interest"]["point2"],
        position_object["home_drone"]["drone2"]
    ],
    [
        position_object["points_interest"]["point3"],
        position_object["home_drone"]["drone3"]
    ]

]

# взлет всех дронов
for drone in drones:
    drone.arm()
    drone.takeoff()

# Разрешение лететь каждому дрону
new_point = [True, True, True, True]
while True:

    fin = 0
    for i in range(len(drones)):

        if new_point[i]:
            new_point[i] = False
            current_point = mission_for_drone[i].pop(0)
            drones[i].go_to_local_point(*current_point)

        if drones[i].point_reached():
            print('new_point', i)
            if len(mission_for_drone[i]) == 0:
                fin += 1
                continue

            new_point[i] = True

        if fin == 4:
            print('break')
            break
        fin = 0

