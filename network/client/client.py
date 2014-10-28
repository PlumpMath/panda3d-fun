#!/usr/bin/env python

import logging
import sys
import argparse

import protocol

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (KeyboardButton,
                          QueuedConnectionManager,
                          QueuedConnectionReader,
                          ConnectionWriter,
                          Datagram
                          )


class GlobalClockMixin(object):

    def get_dt(self):
        """
        :returns int: elapsed time for the previous frame
        """
        return self.base.taskMgr.globalClock.get_dt()


class TaskMixin(object):

    @property
    def task_manager(self):
        task_manager = self.taskMgr if hasattr(self, 'taskMgr') else self.base.taskMgr
        return task_manager

    def add_task(self, callback, name=None, sort=None, extra_args=None, append_task=None):
        """
        :param func callback: callback the task manager should execute
        :param str name: name to assign the task
        :param int sort: sort value to assign task, lower sort values run before tasks with
                         higher sort values
        :param list extra_args: list of arguments to pass to the task callback
        :param bool append_task: if `True` task object will be appended to :attr:`extra_args`
        """
        self.task_manager.add(
            callback,
            name=name,
            sort=sort,
            extraArgs=extra_args,
            appendTask=append_task,
        )


class Player(GlobalClockMixin, TaskMixin):

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


class Connection(GlobalClockMixin, TaskMixin):

    def __init__(self, base, host, port):
        self.base = base
        self.host = host
        self.port = port

        self._conn = None

        self._retry_elapsed = 0
        self._retry_next = 0
        self._data_last_received = 0

        self.manager = QueuedConnectionManager()

        self.reader = QueuedConnectionReader(
            self.manager,
            0,  # number of threads
        )

        # we're using our own protocol so we don't want panda reading our headers and getting
        # all foobared by it (not setting raw mode causes `dataAvailable` to block
        # once there is actually data to process)
        self.reader.setRawMode(True)

        self.writer = ConnectionWriter(
            self.manager,
            0,  # number of threads
        )

    def connect(self, connected_callback, task):
        """
        Attempts to connect to the server and if unable to will retry adding
        a second to the wait time to each consecutive failure.
        """
        self._retry_elapsed += self.get_dt()
        if self._retry_elapsed < self._retry_next:
            return task.cont

        logging.debug(
            'attempting to connect to server at %s:%d',
            self.host,
            self.port
        )
        self._conn = self.manager.openTCPClientConnection(
            self.host,
            self.port,
            10000,  # timeout ms
        )

        if self._conn:
            logging.debug('connection established')
            self.reader.addConnection(self._conn)

            # reset the counters in case the connection drops and we have to restart the
            # connection process
            self._retry_elapsed = 0
            self._retry_next = 0

            # add a task to poll the connection for data
            self.add_task(
                self.task_read_polling,
                name='connection_reader_poll',
                sort=-39,
            )

            connected_callback()
            return

        # no connection so retry in a bit
        self._retry_elapsed = 0
        if self._retry_next == 0:
            self._retry_next = 1
        elif self._retry_next > 9:
            self._retry_next = 10
        else:
            self._retry_next += 1

        logging.error(
            'Unable to connect to server %s:%s, will retry in %d seconds',
            self.host,
            self.port,
            self._retry_next,
        )
        return task.cont

    def task_read_polling(self, task):
        if self.reader.dataAvailable():
            logging.debug('data available from server')
            datagram = Datagram()
            if self.reader.getData(datagram):
                logging.debug('received data from server: %s', datagram)
                logging.debug('received data from server: %s', datagram.getMessage())
                # TODO: provide a way to supply a data callback
            self._data_last_received = 0
        else:
            # no data received
            logging.debug('no data')
            self._data_last_received += self.get_dt()

        if self._data_last_received >= 10:
            logging.error('connection to server lost')
            return

        return task.cont

    def shutdown(self):
        logging.info('connection reader shutting down')
        self.reader.shutdown()


class Client(ShowBase, TaskMixin):

    def __init__(self, host, port):
        ShowBase.__init__(self)

        # bind the escape key to close the client
        self.accept('escape', self.close)

        self.conn = Connection(self, host, port)
        self.add_task(
            self.conn.connect,
            name='connect_to_server',
            extra_args=[self.connected],
            append_task=True,
        )

    def connected(self):
        logging.debug('creating player')
        self.player = Player(self)

    def close(self):
        logging.info('shutting down...')
        # TODO: close connection gracefully
        self.conn.shutdown()
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
