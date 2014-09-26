from direct.showbase.ShowBase import ShowBase


class Client(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        # self.camera.setPos(0, 0, 0)
        # self.camera.setHpr(10, 0, 0)

        self.cube = self.loader.loadModel('models/cube')
        self.cube.reparentTo(self.render)
        self.cube.setPos(0, 15, -1)
        self.cube.setHpr(20, 10, 0)


client = Client()
client.run()
