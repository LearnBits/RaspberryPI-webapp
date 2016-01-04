from serialport import LBSerialRequest
from threading import Timer
from glob import g
import json

class LBShieldAPI:
    #
    NO_SERIAL = json.dumps({'STATUS':'NO_SERIAL'})
    SHUTDOWN  = json.dumps({'STATUS':'SERVER_SHUTDOWN'})
    ERROR     = json.dumps({'STATUS':'SERIAL_ERROR'})

    def __init__(self):
        pass
    #
    # Synchronous serial requests
    def send_serial_request(self, data):
        if not g.config.use_serial:
            ret_val = LBShieldAPI.NO_SERIAL
        elif not g.alive:
    		ret_val = LBShieldAPI.SHUTDOWN
        else:
            req = LBSerialRequest(data)
            ret_val = req.get_ack() if req.is_ok else LBShieldAPI.ERROR
        return ret_val
    #
    def led_bar8(self, led_values):
        if len(led_values) != 8:
            raise ValueError('LED CMD: must provide exactly 8 LED values %s' % str(led_values))
        led_values = map(lambda x: int(x) if int(x) < 139 else 0, led_values)
        return self.send_serial_request({'CMD':'LED','SET': led_values})

    def motor(self, right, left):
        right = min( max(right, -255), 255)
        left  = min( max(left , -255), 255)
        return self.send_serial_request({'CMD':'MOTOR','MOVE':[right,left]})

    def reset_shield(self):
        ret = self.send_serial_request({'CMD': 'RESET'})
        print 'RESET ok' if ret.has_key('RESP') else ('RESET error: %s' % str(ret))

# Global object
g.api = LBShieldAPI()
