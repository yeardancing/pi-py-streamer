#!/usr/bin/env python

import sys
import Queue
from pipystreamer import PiPyStreamer

q = Queue.Queue()
resp_q = Queue.Queue()

PiPyStreamer(q, resp_q).start()

while True:
    c = sys.stdin.read(2)
    responseNeeded = False

    if c[0] == 'd':
        request = PiPyStreamer.Actions.GET_DURATION
        responseNeeded = True
    elif c[0] == 'g':
        request = PiPyStreamer.Actions.PLAY
    elif c[0] == 'l':
        request = PiPyStreamer.Actions.LOAD
    elif c[0] == 'n':
        request = PiPyStreamer.Actions.STOP 
    elif c[0] == 'p':
        request = PiPyStreamer.Actions.GET_POSITION
        responseNeeded = True
    elif c[0] == 'q':
        request = PiPyStreamer.Actions.QUIT 
    elif c[0] == 's':
        request = PiPyStreamer.Actions.SEEK 
    elif c[0] == 'v':
        request = PiPyStreamer.Actions.SET_VOLUME
    else:
        print 'Unrecognized Command!'
        continue

    q.put(request)
    if responseNeeded:
        response = resp_q.get()
        print response

    if request == PiPyStreamer.Actions.QUIT:
        sys.exit(0)

