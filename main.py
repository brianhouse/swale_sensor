#!/usr/bin/env python3

import time, json, math
from random import random
from collections import deque, OrderedDict
from housepy import config, log, util, animation
from housepy.xbee import XBee
from mongo import db

sensor_data = {}
sensor_rssi = OrderedDict()
labels = []

RANGE = 0, 1023
RANGE = 300, 723

TYPE = "moisture"

def message_handler(response):
    # log.info(response)
    try:
        print(response['sensor'], response['samples'], response['rssi'])
        t = util.timestamp(ms=True)        
        sensor = response['sensor']
        sample = response['samples']  ## just one dimension?
        sample.append(round(sum(sample) / 3))
        rssi = response['rssi']
        data = {'t': t, 'type': TYPE, 'sensor': sensor, 'sample': sample, 'rssi': rssi}
        # print(json.dumps(data, indent=4))
        db.branches.insert(data)
        if sensor not in sensor_data:
            sensor_data[sensor] = deque()
            sensor_rssi[sensor] = None
        sensor_data[sensor].appendleft((t, sample))
        sensor_rssi[sensor] = t, rssi
        if len(sensor_data[sensor]) == 1000:
            sensor_data[sensor].pop()
    except Exception as e:
        log.error(log.exc(e))

def draw():
    t_now = util.timestamp(ms=True)

    # ctx.line3(0., 0., 0., .5, .5, .5)
    # ctx.line(0., 0., .5, .5)

    for s, (sensor, (t, rssi)) in enumerate(sensor_rssi.items()):
        if t_now - t > 3:
            bar = 0.01
        else:
            bar = 1.0 - (max(abs(rssi) - 25, 0) / 100)
        x = (20 + (s * 20)) / ctx.width
        ctx.line(x, .1, x, (bar * 0.9) + .1, color=(0., 0., 0., 0.5), thickness=10)
        if sensor not in labels:
            print("Adding label for sensor %s" % sensor)
            labels.append(sensor)
            ctx.label(x, .05, str(sensor), font="Monaco", size=10, width=10, center=True)

    for sensor in list(sensor_data):
        samples = sensor_data[sensor]
        if len(samples):
            # ctx.lines([((t_now - sample[0]) / 10.0, (sample[1][0] - RANGE[0]) / (RANGE[1] - RANGE[0])) for sample in list(samples)], color=(1., 0., 0., 1.))
            # ctx.lines([((t_now - sample[0]) / 10.0, (sample[1][1] - RANGE[0]) / (RANGE[1] - RANGE[0])) for sample in list(samples)], color=(0., 1., 0., 1.))
            ctx.lines([((t_now - sample[0]) / 10.0, (sample[1][2] - RANGE[0]) / (RANGE[1] - RANGE[0])) for sample in list(samples)], color=(0., 0., 1., 1.))
            # ctx.lines([((t_now - sample[0]) / 10.0, (sample[1][3] - RANGE[0]) / (RANGE[1] - RANGE[0])) for sample in list(samples)], color=(0., 0., 0., 1.))


xbee = XBee(config['device_name'], message_handler=message_handler)
ctx = animation.Context(1000, 300, background=(1., 1., 1., 1.), fullscreen=False, title="SWALE", smooth=True)    
ctx.start(draw)
