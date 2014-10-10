#!/usr/bin/env python2

import logging
import sys
import argparse

from direct.showbase.ShowBase import ShowBase
from panda3d.core import KeyboardButton, QueuedConnectionManager, QueuedConnectionReader


class Player(object):

    model_path = 'models/cube01'
    speed = 10

    def __init__(self, base):
        self.base = base
        self.forward = KeyboardButton.ascii_key('w')
        self.backward = KeyboardButton.ascii_key('s')
        self.left = KeyboardButton.ascii_key('a')
        self.right = KeyboardButton.ascii_key('d')

        self.node = self.base.loader.loadModel(self.model_path)
        self.node.reparentTo(self.base.render)

        # set initial position
        # x, y, z
        self.set_pos(0, 15, -1)
        self.set_rot(20, 10, 0)

        # create a task to check for movement
        self.add_task(self.check_movement, 'detect_player_movement')

    def add_task(self, callback, name):
        """
        :param func callback: callback the task manager should execute
        :param str name: name to assign the task
        """
        self.base.taskMgr.add(callback, name)

    def get_x(self):
        """
        :returns float: x coordinate for node
        """
        return self.node.getX()

    def get_y(self):
        """
        :returns float: y coordinate for node
        """
        return self.node.getY()

    def get_dt(self):
        """
        :returns int: elapsed time for the previous frame
        """
        return self.base.taskMgr.globalClock.get_dt()

    def set_pos(self, x, y, z):
        """
        :param float x: x coordinate
        :param float y: y coordinate
        :param float z: z coordinate
        """
        self.node.setPos(x, y, z)

    def set_x(self, x):
        """
        :param float x: x coordinate
        """
        self.node.setX(x)

    def set_y(self, y):
        """
        :param float y: y coordinate
        """
        self.node.setY(y)

    def set_rot(self, h, p, r):
        """
        :param float h: heading angle
        :param float p: pitch angle
        :param float r: roll angle
        """
        self.node.setHpr(h, p, r)

    def check_movement(self, task):
        if self.is_down(self.forward) or self.is_down(self.backward):
            current_y = self.get_y()
            logging.debug('current y: %s', current_y)
            mod = 1 if self.is_down(self.forward) else -1
            new_y = self.speed * mod * self.get_dt() + current_y
            logging.debug('new y: %s', new_y)
            self.set_y(new_y)
        if self.is_down(self.left) or self.is_down(self.right):
            current_x = self.get_x()
            logging.debug('current x: %s', current_x)
            mod = 1 if self.is_down(self.right) else -1
            new_x = self.speed * mod * self.get_dt() + current_x
            logging.debug('new x: %s', new_x)
            self.set_x(new_x)

        return task.cont

    @property
    def is_down(self):
        return self.base.mouseWatcherNode.is_button_down


class Client(ShowBase):

    def __init__(self, server_host, server_port):
        ShowBase.__init__(self)
        self.server_host = server_host
        self.server_port = server_port

        # bind the escape key to close the client
        self.accept('escape', self.close)

        self.conn_manager = QueuedConnectionManager()
        self.conn_reader = QueuedConnectionReader(self.conn_manager, 0)
        logging.debug(
            'attempting to connect to server at %s:%d',
            self.server_host,
            self.server_port
        )
        self.conn = self.conn_manager.openTCPClientConnection(
            self.server_host,
            self.server_port,
            10000,
        )
        if self.conn:
            logging.debug('connection established')
            self.conn_reader.addConnection(self.conn)
            # add the player to the scene
            self.player = Player(self)

    def close(self):
        logging.info('shutting down...')
        sys.exit(0)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='client options')
    parser.add_argument('--host', dest='host', default='localhost',
                        help='server hostname/ip address (default: localhost)')
    parser.add_argument('--port', dest='port', type=int, default=10000,
                        help='server port (default: 10000)')
    args = parser.parse_args()

    logging.info('starting...')
    client = Client(args.host, args.port)
    client.run()
