import os 
import sys
import threading
import Queue
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
Gst.init(None)

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
        player.set_state(Gst.State.NULL)
        print "playing:", uri
        player.set_property('uri', 'file://' + os.path.abspath(uri))
        player.set_state(Gst.State.PLAYING)

    def run(self):
        pl = Gst.ElementFactory.make('playbin', 'player')

        while True:
            message = pl.get_bus().timed_pop_filtered(200 * Gst.MSECOND, 
                    Gst.MessageType.STATE_CHANGED | Gst.MessageType.ERROR | Gst.MessageType.EOS)
            if message:
                if message.type == Gst.MessageType.ERROR:
                    err, debug = message.parse_error()
                    print("Error received from element %s: %s" % (
                    message.src.get_name(), err))
                    print("Debugging information: %s" % debug)
                    break
                elif message.type == Gst.MessageType.EOS:
                    print("End-Of-Stream reached.")
                    pl.set_state(Gst.State.NULL)
                    break
                elif message.type == Gst.MessageType.STATE_CHANGED:
                    if isinstance(message.src, Gst.Pipeline):
                        old_state, new_state, pending_state = message.parse_state_changed()
                        print("Pipeline state changed from %s to %s." %
                            (old_state.value_nick, new_state.value_nick))
                else:
                    print message.type
                    print("Unexpected message received.")

            try:
                try:
                    item = self.q.get(True, 1.0)
                    c = item[0]
                except:
                    continue

                if c == PiPyStreamer.SEEK:
                    try:
                        loc = float(item[2:])
                        pl.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, loc * Gst.SECOND) 
                    except:
                        print "Couldn't seek"

                elif c == PiPyStreamer.HELP:
                    self.resp_q.put(PiPyStreamer.help_str)
                    self.resp_q.task_done()

                elif c == PiPyStreamer.IS_PLAYING:
                    try:
                        if pl.get_state(timeout = 50 * Gst.MSECOND)[1] == Gst.State.PLAYING:
                            self.resp_q.put(1)
                        else:
                            self.resp_q.put(0)
                    except:
                        self.resp_q.put("Couldn't get play status")
                    self.resp_q.task_done()

                elif c == PiPyStreamer.QUIT:
                    pl.set_state(Gst.State.NULL)
                    print 'bye!'
                    return 

                elif c == PiPyStreamer.GET_DURATION:
                    try: 
                        _, duration = pl.query_duration(Gst.Format.TIME)
                        self.resp_q.put(float(duration) / Gst.SECOND)
                    except:
                        self.resp_q.put("Couldn't fetch song duration")
                    self.resp_q.task_done()

                elif c == PiPyStreamer.GET_POSITION:
                    try:
                        _, current = pl.query_position(Gst.Format.TIME)
                        self.resp_q.put(float(current) / Gst.SECOND)
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
                    pl.set_state(Gst.State.PAUSED)

                elif c == PiPyStreamer.PLAY:
                    pl.set_state(Gst.State.PLAYING)

                elif c == PiPyStreamer.LOAD:
                    self.loadUri(pl, item[2:])
                    
            except IOError: 
                print 'IOerror...'

