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
