#!/usr/bin/env python3

import logging
import argparse
import socket
import functools
import errno

import protocol

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.iostream import IOStream


connections = dict()


def send_heartbeat():
    if len(connections) < 1:
        # skip heartbeat if no connections
        return

    logging.debug('sending heartbeat to %d connection(s)', len(connections))
    for conn_addr in connections:
        stream = connections[conn_addr]
        p = protocol.HeartBeat()
        stream.write(bytes(p))


def clear_connection(conn_addr):
    if conn_addr in connections:
        del connections[conn_addr]
        logging.info('removed closed connection %s (%d)', conn_addr, len(connections))


def connection_ready(sock, fd, events):
    while True:
        try:
            connection, address = sock.accept()
        except socket.error as ex:
            if ex.args[0] not in (errno.EWOULDBLOCK, errno.EAGAIN):
                raise
            return

        connection.setblocking(0)
        stream = IOStream(connection)
        # add callback to handle stream close
        stream.set_close_callback(functools.partial(clear_connection, address))

        connections[address] = stream
        logging.info('accepted connection from %s (%d)', address, len(connections))

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='tornado server options')
    parser.add_argument('--bind-port', dest='bind_port', default='10000', type=int,
                        help='port to bind to (default: 10000)')
    parser.add_argument('--bind-addr', dest='bind_addr', default='127.0.0.1',
                        help='address to bind to (default: 127.0.0.1)')
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(0)
    sock.bind((args.bind_addr, args.bind_port))
    logging.info('binding on %s:%d', args.bind_addr, args.bind_port)
    sock.listen(128)

    io_loop = IOLoop.current()
    callback = functools.partial(connection_ready, sock)
    io_loop.add_handler(sock.fileno(), callback, io_loop.READ)
    heartbeat = PeriodicCallback(send_heartbeat, 2000, io_loop)
    heartbeat.start()

    try:
        io_loop.start()
    except KeyboardInterrupt:
        logging.info('shutting down')
        IOLoop.current().stop()
