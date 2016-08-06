#!/usr/bin/env python

import sys
import Queue
from pipystreamer import PiPyStreamer

q = Queue.Queue()
resp_q = Queue.Queue()

PiPyStreamer(q, resp_q).start()

while True:
    responseNeeded = False

    c = raw_input('\nbooj-player>')

    if not c:
        continue

    if c[0] not in 'dghjlnpqstv':
        print 'Unrecognized Command!'
        continue

    if c[0] in 'dhjpt':
        responseNeeded = True

    q.put(c)
    if responseNeeded:
        response = resp_q.get()
        print response

    if c[0] == PiPyStreamer.QUIT:
        sys.exit(0)

