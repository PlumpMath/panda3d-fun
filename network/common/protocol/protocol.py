from launch import Packet

PROTOCOL = 1000


class Heartbeat(Packet):
    protocol = 1000
    type = 2000
