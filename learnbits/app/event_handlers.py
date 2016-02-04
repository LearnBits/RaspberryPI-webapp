class LBEventHandler:
    def __init__(self, name, statement):
        self.name = name
        self.invoke_statement = statement
        self.func = None

def get_signatures():
  ''' The invoke statements define the function signature '''
  def func_signature(n):
    params = ''
    for i in xrange(n):
        params += ('__p__[%d]'  % i) + (', ' if i < n-1 else '')
    return '__f__(%s)' % params

  return {
    # face_detection(x, y, w, h)
    'FACE_DETECTION': LBEventHandler( 'face_detection', func_signature(4)),

    # ball_tracking(dx, dy)
    'BALL_TRACKING' : LBEventHandler( 'ball_tracking',  func_signature(2)),

    # imu(ax, ay, az, gx, gy, gz)
    'MPU6050' : LBEventHandler( 'imu',					func_signature(6)),

    # temperature_pressure(temperature, pressure)
    'BMP180'  : LBEventHandler( 'temperature_pressure', func_signature(2)),

    # slider(value)
    'SLIDEPOT': LBEventHandler( 'slider', 				func_signature(1)),

    # pre_process()
    'PRE_PROCESS': LBEventHandler( 'pre_process', 		func_signature(0)),

    # post_process()
    'POST_PROCESS': LBEventHandler( 'post_process', 	func_signature(0)),

    # init()
    'INIT': LBEventHandler( 'init', 	                func_signature(0)),

    # cleanup()
    'CLEANUP': LBEventHandler( 'cleanup', 	            func_signature(0))
  }
