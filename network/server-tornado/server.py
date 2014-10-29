#!/usr/bin/env python

import logging
import argparse
import socket
import functools
import errno

from tornado.ioloop import IOLoop


class Server(object):

    def __init__(self, io_loop=None):
        self.bind_host = None
        self.bind_port = None
        self.sock = None
        self.io_loop = io_loop or IOLoop.current()

        self.connections = dict()

    def add_connection(self):
        raise NotImplementedError

    def listen(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setblocking(0)
        self.sock.bind((self.host, self.port))
        logging.info('Listening on %s:%d', self.host, self.port)

        callback = functools.partial(self.recv, self.sock)
        self.io_loop.add_handler(self.sock.fileno(), callback, self.io_loop.READ)

    def recv(self, sock, fd, events):
        while True:
            try:
                data, address = sock.recvfrom(1024)
                logging.debug('received data: %r, from: %s', data, address)
                self.process_data(data, address)
            except socket.error as ex:
                # EWOULDBLOCK, EAGAIN - An operation that would block was attempted on an
                # object that has non-blocking mode selected. Trying the same operation again
                # will block until some external condition makes it possible to read, write, or
                # connect. Resource temporarily unavailable; the call might work if you try
                # again later.
                if ex.args[0] not in (errno.EWOULDBLOCK, errno.EAGAIN):
                    raise
                return

    def process_data(self, data, address):
        raise NotImplementedError

    def shutdown(self):
        logging.info('Shutting down')
        self.sock.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='tornado server options')
    parser.add_argument('--bind-port', dest='bind_port', default='10000', type=int,
                        help='port to bind to (default: 10000)')
    parser.add_argument('--bind-addr', dest='bind_addr', default='127.0.0.1',
                        help='address to bind to (default: 127.0.0.1)')
    args = parser.parse_args()

    io_loop = IOLoop.current()
    server = Server(io_loop)
    try:
        server.listen(args.bind_addr, args.bind_port)
        io_loop.start()
    except KeyboardInterrupt:
        server.shutdown()
        io_loop.stop()
