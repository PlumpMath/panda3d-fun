import logging

from direct.showbase.ShowBase import ShowBase


class Player(object):
    pass


class Client(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        self.speed = 5

        self.cube = self.loader.loadModel('models/cube01')
        self.cube.reparentTo(self.render)
        # x, y, z
        self.cube.setPos(0, 15, -1)
        self.cube.setHpr(20, 10, 0)

        self.accept('w', self.move_forward)

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
