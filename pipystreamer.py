import os 
import sys
import threading
import Queue
import pygst
pygst.require ("0.10")
import gst

class PiPyStreamer(threading.Thread):
    GET_DURATION    = 'd'
    PLAY            = 'g'
    HELP            = 'h'
    IS_PLAYING      = 'j'
    LOAD            = 'l'
    STOP            = 'n'
    GET_POSITION    = 'p'
    QUIT            = 'q'
    SEEK            = 's'
    GET_VOLUME      = 't'
    SET_VOLUME      = 'v' 
    
    help_str = '''
       d            - get duration
       g            - play
       h            - this help
       j            - is playing
       l <file>     - load song
       n            - stop
       p            - get position
       q            - quit
       s <position> - seek
       t            - get volume
       v <volume>   - set volume'''

    def __init__(self, requestQueue, responseQueue):
        threading.Thread.__init__(self)
        self.q = requestQueue
        self.resp_q = responseQueue

    def loadUri(self, player, uri):
        player.set_state(gst.STATE_NULL)
        print "playing:", uri
        player.set_property('uri', 'file://' + os.path.abspath(uri))
        player.set_state(gst.STATE_PLAYING)

    def run(self):
        pl = gst.element_factory_make("playbin", "player")

        while True:
            msg = pl.get_bus().timed_pop_filtered(1, gst.MESSAGE_EOS)
            if msg:
                print "End of playback!"
            try:
                try:
                    item = self.q.get(True, 1.0)
                    c = item[0]
                except:
                    continue

                if c == PiPyStreamer.SEEK:
                    try:
                        loc = float(item[2:])
                        pl.seek_simple(gst.FORMAT_TIME, gst.SEEK_FLAG_FLUSH | gst.SEEK_FLAG_KEY_UNIT, loc * gst.SECOND) 
                    except:
                        print "Couldn't seek"

                elif c == PiPyStreamer.HELP:
                    self.resp_q.put(PiPyStreamer.help_str)
                    self.resp_q.task_done()

                elif c == PiPyStreamer.IS_PLAYING:
                    try:
                        if pl.get_state()[1] == gst.STATE_PLAYING:
                            self.resp_q.put(1)
                        else:
                            self.resp_q.put(0)
                    except:
                        self.resp_q.put("Couldn't get play status")
                    self.resp_q.task_done()

                elif c == PiPyStreamer.QUIT:
                    pl.set_state(gst.STATE_NULL)
                    print 'bye!'
                    return 

                elif c == PiPyStreamer.GET_DURATION:
                    try: 
                        duration, format = pl.query_duration(gst.FORMAT_TIME)
                        self.resp_q.put(float(duration) / gst.SECOND)
                    except:
                        self.resp_q.put("Couldn't fetch song duration")
                    self.resp_q.task_done()

                elif c == PiPyStreamer.GET_POSITION:
                    try:
                        position, format = pl.query_position(gst.FORMAT_TIME)
                        self.resp_q.put(float(position) / gst.SECOND)
                    except:
                        self.resp_q.put("Couldn't fetch song position")
                    self.resp_q.task_done()

                elif c == PiPyStreamer.SET_VOLUME:
                    try:
                        vol = float(item[2:])
                        pl.set_property('volume', vol)
                    except:
                        print "Couldn't set volume"

                elif c == PiPyStreamer.GET_VOLUME:
                    try:
                        vol = pl.get_property('volume')
                        self.resp_q.put(vol)
                    except:
                        self.resp_q.put("Couldn't get volume")
                    self.resp_q.task_done()

                elif c == PiPyStreamer.STOP:
                    pl.set_state(gst.STATE_PAUSED)

                elif c == PiPyStreamer.PLAY:
                    pl.set_state(gst.STATE_PLAYING)

                elif c == PiPyStreamer.LOAD:
                    self.loadUri(pl, item[2:])
                    
            except IOError: 
                print 'IOerror...'

