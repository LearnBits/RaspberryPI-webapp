# lights
colors = [[1]*8, [64]*8, [101]*8]
led8_start_ticks = 0
# dancing
total_dance_ticks = 0
dance_step_ticks = 0
dancing_step = 0
steps = [[4, 88, -88],[8, -88, 88],[8, 88, -88],[8, -88, 88],[8, 88, -88],[4, -88, 88],[8, -100, -100],[24, 50, 50]]
def move():
    global ticks, total_dance_ticks, dance_step_ticks, dancing_step, steps, led8_start_ticks
    if total_dance_ticks > ticks:
        if dance_step_ticks == ticks:
            pi.motor(steps[dancing_step][1], steps[dancing_step][2])
            dance_step_ticks = ticks + steps[dancing_step][0]
            dancing_step += 1
        if (ticks - led8_start_ticks) % 10 == 0:
            pi.led_bar8(colors[(collisions + ticks) % len(colors)])
    else:
        pi.motor(0, 0)
        pi.led_bar8_off()

def start_reaction():
    global ticks, collisions, no_events_ticks
    global colors, led8_start_ticks
    global dancing_step, total_dance_ticks, dance_step_ticks, steps
    global move, light
    # motors
    dancing_step = 0
    total_dance_ticks = ticks + reduce(lambda x,y: [x[0]+y[0],x[1],y[1]], steps)[0]
    dance_step_ticks = ticks

    # led_bar8
    led8_start_ticks = ticks
    no_events_ticks = max(led8_start_ticks, total_dance_ticks) + 20
    move()


A_T_1 = 2300.0
G_T_1 = 85.0
ticks = 0
no_events_ticks = 0
collisions = 1
def imu(ax,ay,az,gx,gy,gz):
    global A_T_1, G_T_1, collisions, ticks, led8_ticks, total_dance_ticks, no_events_ticks
    global start_reaction, move, light
    ticks += 1
    if ticks > no_events_ticks:
        aa = math.sqrt(ax*ax + ay*ay + az*az)
        ag = math.sqrt(gx*gx + gy*gy + gz*gz)
        if aa > A_T_1 or ag > G_T_1:
            start_reaction()
            collisions += 1
    else:
        # Note >= comparison is needed
        if total_dance_ticks >= ticks:  move()
