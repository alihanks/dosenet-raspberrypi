#!/usr/bin/env python
import argparse

import kromek

import numpy as np


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--transport', '-t', dest='transport', default='any')
    parser.add_argument('--interval', '-i', dest='interval', default=30)
    parser.add_argument('--count', '-c', dest='count', default=0)
    parser.add_argument('--device', '-d', dest='device', default='all')
    parser.add_argument('--log-bytes', '-b', dest='log_bytes', default=False, action='store_true')
    args = parser.parse_args()
    
    total = None
    lst = None
    flag = True

    interval = int(args.interval)
    count = int(args.count)

    if args.transport == 'any':
        devs = kromek.discover()
    else:
        devs = kromek.discover(args.transport)
    print 'Discovered %s' % devs
    if len(devs) <= 0:
        return

    filtered = []
    for dev in devs:
        if args.device == 'all' or dev[0] in args.device:
            filtered.append(dev)

    devs = filtered
    if len(devs) <= 0:
        return

    done_devices = set()
    with kromek.Controller(devs, interval) as controller:
        for reading in controller.read():
            if flag:
                total = np.array(reading[4])
                lst = np.array([reading[4]])
                flag = False
            else:
                total += np.array(reading[4])
                lst = np.concatenate((lst, [np.array(reading[4])]))
                print(len(lst))
            serial = reading[0]
            dev_count = reading[1]
            if serial not in done_devices:
                #print reading[4]
                #print total
                print lst
            if dev_count >= count > 0:
                done_devices.add(serial)
                controller.stop_collector(serial)
            if len(done_devices) >= len(devs):
                break


if __name__ == '__main__':
    main()
