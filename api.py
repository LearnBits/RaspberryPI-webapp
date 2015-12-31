from serialport import LBSerialRequest
from threading import Timer
from glob import g

class LBShieldAPI:
    #
    def __init__(self):
        pass
    #
    # Synchronous serial requests
    def send_serial_request(self, data):
        if not g.config.use_serial:
            return {'STATUS':'NO_SERIAL'}
        elif not g.alive:
    		return {'STATUS':'SERVER_SHUTDOWN'}
        else:
        	req = LBSerialRequest(data)
        	return req.get_ack() if req.is_ok else {'STATUS':'SERIAL_ERROR'}
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
        ret = self.send_serial_request({CMD: 'RESET'})
        print 'RESET ok' if ret.has_key('RESP') else ('RESET error: %s' % str(ret))

# Global object
g.api = LBShieldAPI()
