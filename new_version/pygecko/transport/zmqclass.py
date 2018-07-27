##############################################
# The MIT License (MIT)
# Copyright (c) 2014 Kevin Walchko
# see LICENSE for full details
##############################################
#
# Kevin J. Walchko 13 Oct 2014
#
# see http://zeromq.org for more info
# http://zguide.zeromq.org/py:all

from __future__ import print_function
from __future__ import division
import zmq
from zmq.devices import ProcessProxy
import time
import socket as Socket
import msgpack


class ZMQError(Exception):
    pass


class Base(object):
    """
    Base class for other derived pub/sub/service classes
    """
    # ctx = zmq.Context()
    socket = None
    pack = None

    def __init__(self):
        self.ctx = zmq.Context()

    def __del__(self):
        self.ctx.term()
        print('[<] shutting down {}'.format(type(self).__name__))

    def bind(self, addr, hwm=None):
        """
        Binds a socket to an addr. Only one socket can bind.
        Usually pub binds and sub connects, but not always!

        in: addr as tcp or uds, hwm (high water mark) a int that limits buffer length
        out: none
        """
        print(type(self).__name__, 'bind to {}'.format(addr))
        self.socket.bind(addr)
        if hwm:
            self.socket.set_hwm(hwm)

    def connect(self, addr, hwm=None):
        """
        Connects a socket to an addr. Many different sockets can connect.
        Usually pub binds and sub connects, but not always!

        in: addr as tcp or uds, hwm (high water mark) a int that limits buffer length
        out: none
        """
        print(type(self).__name__, 'connect to {}'.format(addr))
        self.socket.connect(addr)
        if hwm:
            self.socket.set_hwm(hwm)


class Pub(Base):
    """
    Simple publisher
    """
    def __init__(self, pack=None):
        """
        Publishes messages on a topic.

        in: pack - function to serialize messages if needed
        """
        Base.__init__(self)

        try:
            self.socket = self.ctx.socket(zmq.PUB)
            # self.socket.set_hwm(hwm)
            # self.socket.setsockopt(zmq.SNDHWM, 1)

        except Exception as e:
            error = '[-] Pub Error, {0!s}'.format((str(e)))
            raise ZMQError(error)

        if pack:
            self.pack = pack

    def __del__(self):
        self.socket.close()

    def pub(self, topic, msg):
        """
        in: topic, message
        out: none
        """
        # jmsg = serialize(msg)
        if self.pack:
            jmsg = msgpack.packb(msg, default=self.pack, use_bin_type=True, strict_types=True)
        else:
            jmsg = msgpack.packb(msg, use_bin_type=True, strict_types=True)
        # self.socket.send_multipart([topic.encode('ascii'), jmsg.encode('ascii')])
        done = True
        while done:
            done = self.socket.send_multipart([topic.encode('ascii'), jmsg])
            # done = self.socket.send(jmsg)
        # print('pub >>', topic.encode('ascii'))

    def raw_pub(self, topic, msg):
        done = True
        while done:
            done = self.socket.send_multipart([topic.encode('ascii'), msg])


class Sub(Base):
    """
    Simple subscriber that read messages on a topic(s)
    """
    unpack = None

    def __init__(self, topics=None, unpack=None):
        """
        topics: an array of topics, ex ['hello', 'cool messages']
        unpack: a function to deserialize messages if necessary
        """
        Base.__init__(self)
        # if type(topics) is list:
        #     pass
        # else:
        #     raise Exception('topics must be a list')
            # topics = [topics]

        # self.topics = topics
        try:
            self.socket = self.ctx.socket(zmq.SUB)
            # self.socket.set_hwm(hwm)  # set high water mark, so imagery doesn't buffer and slow things down

            # manage subscriptions
            # can also use: self.socket.subscribe(topic) or unsubscribe()
            if topics is None:
                print("[>] Receiving messages on ALL topics...")
                self.socket.setsockopt(zmq.SUBSCRIBE, b'')
                self.topics = b''
            else:
                if type(topics) is list:
                    pass
                else:
                    raise Exception('topics must be a list')
                self.topics = topics
                for t in topics:
                    print("[>] Subscribed to messages on topics: {} ...".format(t))
                    # self.socket.setsockopt(zmq.SUBSCRIBE, t.encode('ascii'))
                    self.socket.setsockopt(zmq.SUBSCRIBE, t.encode('ascii'))

        except Exception as e:
            error = '[-] Sub Error, {0!s}'.format((str(e)))
            # print error
            raise ZMQError(error)

        if unpack:
            self.unpack = unpack

    def __del__(self):
        if self.topics is None:
            self.socket.setsockopt(zmq.UNSUBSCRIBE, b'')
        else:
            for t in self.topics:
                self.socket.setsockopt(zmq.UNSUBSCRIBE, t.encode('ascii'))
        self.socket.close()

    def recv(self, flags=0):
        """
        flags=zmq.NOBLOCK to implement non-blocking
        """
        topic = None
        msg = None
        try:
            topic, jmsg = self.socket.recv_multipart(flags=flags)
            if self.unpack:
                msg = msgpack.unpackb(jmsg, ext_hook=self.unpack, raw=False)
            else:
                msg = msgpack.unpackb(jmsg, raw=False)
        except zmq.Again as e:
            # no message has arrived yet
            print(e)
            pass
        except Exception as e:
            # something else is wrong
            print(e)
            raise
        return topic, msg

    def raw_recv(self, flags=0):
        return self.socket.recv_multipart(flags=flags)

    # def recv(self):
    #     # check to see if there is read, write, or erros
    #
    #     topic = None
    #     msg = None
    #
    #     zmq.zmq_poll([(self.socket, zmq.POLLIN,)], 10)
    #     socks = self.poller.poll(10)
    #     print('socks', socks)
    #     socks = dict(socks)
    #     topic, jmsg = self.socket.recv_multipart()
    #     print(topic)
    #
    #     print('socks:', socks)
    #
    #     cnt = 0
    #     if socks.get(self.socket) == zmq.POLLIN:
    #         print('pollin:')
    #         try:
    #             for i in range(10):
    #                 topic, jmsg = self.socket.recv_multipart()
    #                 msg = deserialize(jmsg)
    #                 cnt = i
    #         except:
    #             pass
    #
    #         print('recv looped', cnt)
    #     # print(topic, msg)
    #
    #     return topic, msg


# class ServiceProvider(Base):
#     """
#     Provides a service
#     """
#     def __init__(self, bind_to):
#         Base.__init__(self)
#         self.socket = self.ctx.socket(zmq.REP)
#         # tcp = 'tcp://' + bind_to[0] + ':' + str(bind_to[1])
#         tcp = self.getAddress(bind_to)
#         self.socket.bind(tcp)
#
#     def __del__(self):
#         self.socket.close()
#         self._stop()
#
#     def listen(self, callback):
#         # print 'listen'
#         while True:
#             jmsg = self.socket.recv()
#             msg = json.loads(jmsg)
#
#             ans = callback(msg)
#
#             jmsg = json.dumps(ans)
#             self.socket.send(jmsg)
#
#
# class ServiceClient(Base):
#     """
#     Client socket to get a response back from a service provider
#     """
#     def __init__(self, bind_to):
#         Base.__init__(self)
#         self.socket = self.ctx.socket(zmq.REQ)
#         # tcp = 'tcp://' + bind_to[0] + ':' + str(bind_to[1])
#         tcp = self.getAddress(bind_to)
#         self.socket.connect(tcp)
#
#     def __del__(self):
#         self.socket.close()
#         self._stop()
#
#     def get(self, msg):
#         jmsg = json.dumps(msg)
#         self.socket.send(jmsg)
#         jmsg = self.socket.recv()
#         msg = json.loads(jmsg)
#         return msg
