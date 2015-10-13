import os 
import sys
import threading
import Queue
import gobject
gobject.threads_init ()
import pygst
pygst.require ("0.10")
import gst

def enum(*sequential, **named):
    enums = dict(zip((sequential), range(len(sequential))), **named)
    return type('Enum', (), enums)

class GenericException(Exception):
    pass

class PiPyStreamer(threading.Thread):
    Actions = enum( 'GET_DURATION', 
                    'GET_POSITION', 
                    'LOAD', 
                    'PLAY', 
                    'QUIT', 
                    'SEEK', 
                    'SET_VOLUME', 
                    'STOP' )

    def __init__(self, requestQueue, responseQueue):
        threading.Thread.__init__(self)
        self.q = requestQueue
        self.resp_q = responseQueue

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

        while True:
            #msg = bus.poll(gst.MESSAGE_STREAM_STATUS, 1.0)
            #if msg:
            #    print msg
            try:
                try:
                    c = self.q.get(True, 2.0)
                except Queue.Empty:
                    continue

                if c == PiPyStreamer.Actions.SEEK:
                    pl.seek_simple(gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH | gst.SEEK_FLAG_KEY_UNIT, 230 * gst.SECOND) 
                elif c == PiPyStreamer.Actions.QUIT:
                    pl.set_state(gst.STATE_NULL)
                    print 'bye!'
                    return 
                elif c == PiPyStreamer.Actions.GET_DURATION:
                    try: 
                        duration, format = pl.query_duration(gst.FORMAT_TIME)
                        self.resp_q.put(float(duration) / gst.SECOND)
                        self.resp_q.task_done()
                    except:
                        raise GenericException("Couldn't fetch song duration")
                elif c == PiPyStreamer.Actions.GET_POSITION:
                    try:
                        position, format = pl.query_position(gst.FORMAT_TIME)
                        self.resp_q.put(float(position) / gst.SECOND)
                        self.resp_q.task_done()
                    except:
                        raise GenericException("Couldn't fetch song position")
                elif c == PiPyStreamer.Actions.SET_VOLUME:
                    try:
                        pl.set_property('volume', 0.1)
                    except:
                        raise GenericException("couldn't set volume")
                elif c == PiPyStreamer.Actions.STOP:
                    pl.set_state(gst.STATE_PAUSED)
                elif c == PiPyStreamer.Actions.PLAY:
                    pl.set_state(gst.STATE_PLAYING)
                elif c == PiPyStreamer.Actions.LOAD:
                    pl.set_state(gst.STATE_NULL)
                    pl.set_property('uri','file://'+os.path.abspath('/home/dspadaro/wonderful.mp3'))
                    pl.set_state(gst.STATE_PLAYING)
                    
            except IOError: 
                print 'IOerror...'

