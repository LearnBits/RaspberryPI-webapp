from Queue  import Queue, Empty
from glob   import g
import json


# Streaming data request from serial port
# global variables for data streams

class LBServerSideEvent:
    # static members
    count = 0
    state = {}
    mimetype = 'text/event-stream'
    #
    def __init__(self):
        # creat event queue
        self.queue = Queue()
        g.dispatcher.add_listener(self.queue)
        # Init stream
        self.id = LBServerSideEvent.count
        LBServerSideEvent.count +=1
        LBServerSideEvent.state[self.id] = True

    def generator(self):
        yield 'event: start\n' + 'data: %d\n\n' % self.id
        #initial i2c scan
        yield 'event: scan\n' + 'data: %s\n\n' % json.dumps(g.serial.get_I2C_list())
        # sampling loop
        while LBServerSideEvent.state[self.id] and g.alive:
            try:
                event_type, json_msg = self.queue.get(timeout=5)
                if event_type == 'SAMPLE':
                    #print 'Sending SSE sample %s' % json_sample
                    yield 'data: %s\n\n' % json_msg
                elif event_type == 'SCAN':
                    yield 'event: scan\n' + 'data: %s\n\n' % json_msg
                else:
                    print 'SSE stream: unknow event %s' % event_type
            except Empty as e:
                print 'Empty queue in streaming data %s. Possibly timed out (5s)' % str(e)
        #
        # end of streaming thread
        yield 'event: close\n' + 'data: {"time": "now"}\n\n'
        g.dispatcher.remove_listener(self.queue)
        print 'Data streaming thread .... done'
