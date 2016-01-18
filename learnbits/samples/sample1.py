px = py = 0
d = 3
ew = ns = ''

def ball_tracking(dx, dy):
    print '(%d , %d)' % (dx,dy)

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
