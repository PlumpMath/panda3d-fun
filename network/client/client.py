import logging

from direct.showbase.ShowBase import ShowBase
from panda3d.core import KeyboardButton
from direct.task import Task


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
        if self.is_down(self.forward):
            logging.debug('moving forward')
            current_y = self.get_y()
            logging.debug('current y: %s', current_y)
            y_delta = self.speed * self.get_dt() + current_y
            logging.debug('new y: %s', y_delta)
            self.set_y(y_delta)
        if self.is_down(self.backward):
            logging.debug('moving backward')
            current_y = self.get_y()
            logging.debug('current y: %s', current_y)
            y_delta = (self.speed * -1) * self.get_dt() + current_y
            logging.debug('new y: %s', y_delta)
            self.set_y(y_delta)
        if self.is_down(self.left):
            logging.debug('moving left')
            current_x = self.get_x()
            logging.debug('current x: %s', current_x)
            x_delta = (self.speed * -1) * self.get_dt() + current_x
            logging.debug('new x: %s', x_delta)
            self.set_x(x_delta)
        if self.is_down(self.right):
            logging.debug('moving right')
            current_x = self.get_x()
            logging.debug('current x: %s', current_x)
            x_delta = self.speed * self.get_dt() + current_x
            logging.debug('new x: %s', x_delta)
            self.set_x(x_delta)

        return Task.cont

    @property
    def is_down(self):
        return self.base.mouseWatcherNode.is_button_down


class Client(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        # add the player to the scene
        self.player = Player(self)

        # self.accept('w', self.move_forward)

    def move_forward(self):
        logging.debug('moving forward')
        current_y = self.cube.getY()
        y_delta = self.speed * self.taskMgr.globalClock.get_dt() + current_y
        logging.debug('y: %s', y_delta)
        self.cube.setY(y_delta)


client = Client()
logging.basicConfig(level=logging.DEBUG)
logging.debug('starting...')
client.run()
