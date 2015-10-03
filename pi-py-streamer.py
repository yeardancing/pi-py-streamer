#!/usr/bin/env python
import gobject
gobject.threads_init ()
import pygst
pygst.require ("0.10")
import gst
import time
import os, sys, threading, Queue

q = Queue.Queue()
resp_q = Queue.Queue()

class GenericException(Exception):
    pass

class Player(threading.Thread):
    def onMsg(pl, msg):
        if msg.type == gst.MESSAGE_ERROR:
            error, debug = msg.parse_error()
            print error, debug

    def run(self):
        mainloop = gobject.MainLoop()
        pl = gst.element_factory_make("playbin", "player")
        pl.set_property('uri','file://'+os.path.abspath('/home/dspadaro/bola.mp3'))
        pl.set_state(gst.STATE_PLAYING)
        context = mainloop.get_context()
        bus = pl.get_bus()

        time = 0.0

        while True:
            #msg = bus.poll(gst.MESSAGE_STREAM_STATUS, 1.0)
            #if msg:
            #    print msg
            try:
                #c = sys.stdin.read(2)
                c = ''
                print 'listening...'
                try:
                    c = q.get(True, 2.0)
                    print 'got a... ', c[0]
                except Queue.Empty:
                    print 'nothing...'
                    continue

                if c[0] in 'sqdp0152ngl':
                    if c[0] == 's':
                        pl.seek_simple(gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH | gst.SEEK_FLAG_KEY_UNIT, 230 * gst.SECOND) 
                    elif c[0] == 'q':
                        pl.set_state(gst.STATE_NULL)
                        print 'bye!'
                        return 
                    elif c[0] == 'd':
                        try: 
                            duration, format = pl.query_duration(gst.FORMAT_TIME)
                            print 'Duration', duration / gst.SECOND
                        except:
                            raise GenericException("Couldn't fetch song duration")
                    elif c[0] == 'p':
                        try:
                            position, format = pl.query_position(gst.FORMAT_TIME)
                            #print 'position', float(position) / gst.SECOND
                            resp_q.put(float(position) / gst.SECOND)
                            resp_q.task_done()
                        except:
                            raise GenericException("Couldn't fetch song position")
                    elif c[0] == '0':
                        try:
                            pl.set_property('volume', 0.0)
                        except:
                            raise GenericException("couldn't set volume")
                    elif c[0] == '1':
                        try:
                            pl.set_property('volume', 1.0)
                        except:
                            raise GenericException("couldn't set volume")
                    elif c[0] == '5':
                        try:
                            pl.set_property('volume', 0.5)
                        except:
                            raise GenericException("couldn't set volume")
                    elif c[0] == '2':
                        try:
                            pl.set_property('volume', 0.2)
                        except:
                            raise GenericException("couldn't set volume")
                    elif c[0] == 'n':
                        pl.set_state(gst.STATE_PAUSED)
                    elif c[0] == 'g':
                        pl.set_state(gst.STATE_PLAYING)
                    elif c[0] == 'l':
                        pl.set_state(gst.STATE_NULL)
                        pl.set_property('uri','file://'+os.path.abspath('/home/dspadaro/wonderful.mp3'))
                        pl.set_state(gst.STATE_PLAYING)
                    
            except IOError: 
                print 'IOerror...'
            #q.task_done()

Player().start()
while True:
    c = sys.stdin.read(2)
    q.put(c)
    if c[0] == 'q':
        break
    elif c[0] == 'p':
        response = resp_q.get()
        print type(response)
        print response

