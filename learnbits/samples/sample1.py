#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
# IMU sensor lab
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

A_T_1 = 2300.0
A_T_2 = 2400.0
G_T_1 = 85.0
G_T_2 = 90.0

AA = []
AG = []
collisions = 1

def imu(ax,ay,az,gx,gy,gz):
    global A_T_1, A_T_2, G_T_1, G_T_2, AA, AG, collisions
    aa = math.sqrt(ax*ax + ay*ay + az*az)
    ag = math.sqrt(gx*gx + gy*gy + gz*gz)
    if aa > A_T_2:   print '%03d ACCE=%f, ax=%d, ay=%d, az=%d' % (collisions, aa, ax, ay, az)
    elif aa > A_T_1: print '%03d acce=%f, ax=%d, ay=%d, az=%d' % (collisions, aa, ax, ay, az)
    if ag > G_T_2:   print '%03d GYRO=%f, gx=%d, gy=%d, gz=%d' % (collisions, ag, gx, gy, gz)
    elif ag > G_T_1: print '%03d gyro=%f, gx=%d, gy=%d, gz=%d' % (collisions, ag, gx, gy, gz)
    if aa > A_T_1 or ag > G_T_1:
        AA.append(aa)
        AG.append(ag)
        collisions += 1
        if len(AA) > 0 and len(AA) % 10 == 0:
            print
            print 'Acce: avg=%f, std=%f, min=%f, max=%f' % (np.mean(AA), np.std(AA), np.min(AA), np.max(AA))
            print 'Gyro: avg=%f, std=%f, min=%f, max=%f' % (np.mean(AG), np.std(AG), np.min(AG), np.max(AG))
            print
            del AA[:]
            del AG[:]
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#

A_T_1 = 2300.0
A_T_2 = 2400.0
G_T_1 = 85.0
G_T_2 = 90.0

collisions = 1
colors = [[1]*8, [64]*8, [101]*8]
ticks = 0
lights_off = 0

def imu(ax,ay,az,gx,gy,gz):
    global A_T_1, A_T_2, G_T_1, G_T_2, collisions, colors, lights_off, ticks
    ticks += 1
    aa = math.sqrt(ax*ax + ay*ay + az*az)
    ag = math.sqrt(gx*gx + gy*gy + gz*gz)
    if aa > A_T_1 or ag > G_T_1:
        pi.led_bar8(colors[collisions % len(colors)])
        collisions += 1
        lights_off = ticks + 20;
    if ticks == lights_off:
        pi.led_bar8_off()
        lights_off = 0



A_T_1 = 2300.0
A_T_2 = 2400.0

G_T_1 = 85.0
G_T_2 = 90.0

def imu(ax,ay,az,gx,gy,gz):
    global A_T_1, A_T_2, G_T_1, G_T_2
    AA = math.sqrt(ax*ax + ay*ay + az*az)
    AG = math.sqrt(gx*gx + gy*gy + gz*gz)
    if AA > A_T_1 or  AG > G_T_1: print 'small collision : Acce=%f, Gyro=%f' % (AA, AG)
    if AA > A_T_1 and AG > G_T_1: print 'medium collision: Acce=%f, Gyro=%f' % (AA, AG)
    if AA > A_T_2 or  AG > G_T_2: print 'BIG COLLISION   : Acce=%f, Gyro=%f' % (AA, AG)

A_T_1 = 2300.0
A_T_2 = 2400.0

G_T_1 = 85.0
G_T_2 = 90.0

def imu(ax,ay,az,gx,gy,gz):
    global A_T_1, A_T_2, G_T_1, G_T_2
    AA = math.sqrt(ax*ax + ay*ay + az*az)
    AG = math.sqrt(gx*gx + gy*gy + gz*gz)
    if AA > A_T_2: print 'ACCE=%f' % AA
    elif AA > A_T_1: print 'acce=%f' % AA
    if AG > G_T_2: print 'GYRO=%f' % AG
    elif AG > G_T_1: print 'gyro=%f' % AG











# statistical analysis
imu_count = 0
AA = []
AG = []

def imu(ax,ay,az,gx,gy,gz):
    global AA, AG, imu_count
    AA.append(math.sqrt(ax*ax + ay*ay + az*az))
    AG.append(math.sqrt(gx*gx + gy*gy + gz*gz))
    imu_count += 1
    if imu_count % 100 == 0:
        print 'Acce: avg=%f, std=%f, min=%f, max=%f' % (np.mean(AA), np.std(AA), np.min(AA), np.max(AA))
        print 'Gyro: avg=%f, std=%f, min=%f, max=%f' % (np.mean(AG), np.std(AG), np.min(AG), np.max(AG))
        print






#imu_count = 55

def init():
    imu_count = 0


def imu(ax,ay,az,gx,gy,gz):
    global imu_count
    imu_count += 1
    if imu_count % 10 == 0: print imu_count


px = py = 0
d = 3
ew = ns = ''
count = 0
t1 = 20
t2 = 50
red = 3
black = 130

# slider
red = 3
black = 130
old_v = 0
color = [3, 23, 43, 63, 83, 103, 133, 143]
def slider(value):
    global red, black, old_v, color
    if abs(value - old_v) > 10:
        v = map(lambda x: color[x-1] if value*8/2160 >= x else black, range(1,9))
        pi.led_bar8(v)
        old_v = value
############


def ball_tracking(dx, dy):
    def sign(x):
        return 0 if x==0 else int(abs(x)/x)

    global count, t1, t2, red, black, pi
    count += 1
    if count % 10 == 0:
        #print '(%d , %d)' % (dx,dy)
        x1 = sign(dx / t1)
        x2 = sign(dx / t2)
        y1 = sign(dy / t1)
        y2 = sign(dy / t2)
        v = map(lambda x: red if x else black, [x2<0, x1<0, x1>0, x2>0, y2<0, y1<0, y1>0, y2>0])
        api.led_bar8(v)
        #print v


#def init(): print '--> init program %d' % __prog_id__

#def cleanup(): print '--> cleanup program %d' % __prog_id__

def face_detection(x, y, w, h):
#def camera(v):
    #print 'length = ' + length(v)
    #print v
    #return
    global px, py, d, ew, ns
    if px - x > d:
        ew = 'east'
    elif x - px > d:
        ew = 'west'
    else:
        ew = ''
    if py - y > d:
        ns = 'north'
    elif y - py > d:
        ns = 'south'
    else:
        ns = ''
    px = x
    py = y
    sep = '-' if len(ns) * len(ew) > 0 else ''
    print ns + sep + ew

def pre_process():
    print '====>>>> pre'

def post_process():
    print '====>>>> post'

#print '@@@@@ from user program @@@@@'
#print json.dumps(__event__)
#print '@@@@@'
