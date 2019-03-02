#!/usr/bin/env python3

"""Walkie-Talkie Server"""

import argparse
import os  # noqa: F401
import subprocess as sp  # noqa: F401
import sys

from twisted.internet import protocol, reactor
from twisted.python import log

import pywalkie as p  # noqa: F401


class WalkieServer(p.Walkie):
    """Walkie Server

    Implements the protocol.Protocol interface.
    """
    def connectionMade(self):
        self.make_sound('kongas')
        self.child = self.listen()

    def dataReceived(self, data):
        super().dataReceived(data)
        chunk = self.get_chunk(data)
        p.dmsg('Actual Data: %r', chunk[20:])

        if self.is_recording:
            if chunk == p.FIN:
                self.make_sound("apert")
                self.child.kill()
                self.child = self.listen()
                self.ACK()
                return

            self.send_chunk()
        else:
            if chunk == p.FIN:
                self.make_sound("apert")
                self.child.kill()
                self.child = self.record()
                self.ACK()
                return

            if not self.is_flag(chunk):
                self.child.stdin.write(chunk)

            self.SYN()

    def make_sound(self, name):
        """Interface for Event-Triggered Sound Effects"""
        project_dir = '/home/bryan/projects/pywalkie/sounds/'
        fp = project_dir + name + '.wav'
        if os.path.exists(fp):
            sp.Popen(['paplay', fp])


class WalkieFactory(protocol.Factory):
    """Factory Class that Generates WalkieServer Instances"""
    protocol = WalkieServer


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('port', help="The port to listen on.")
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debugging output.')
    args = parser.parse_args()

    try:
        port = int(args.port)
    except ValueError:
        parser.error("Port must be an integer.")

    p.DEBUGGING = args.debug

    log.startLogging(sys.stdout)

    p.dmsg('Starting Walkie Server...')

    reactor.listenTCP(port, WalkieFactory())
    reactor.run()
