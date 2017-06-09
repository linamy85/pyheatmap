#!/usr/bin/env python3

from pyheatmap.heatmap import HeatMap
import sys
import math
import numpy as np
import argparse
from PIL import Image, ImageDraw, ImageFont

import matplotlib.pyplot as plt
from matplotlib.pyplot import Figure, subplot

SHIFT = False

def parse_args():
    parser = argparse.ArgumentParser(description='Click map drawer for socialAR')
    parser.add_argument('-i', '--input', required=True,
                        help='Input file with format .csv')
    parser.add_argument('-s', '--scale', type=float, default=1.0,
                        help='Scale for the graph (affects size)')

    return parser.parse_args()

def toPhi(deg):
    return 2 * math.pi * deg / 360

def toxy(shift, rad, deg):
    phi = toPhi(deg)
    return (shift[0] + rad * math.cos(phi), shift[1] - rad * math.sin(phi))

def main(opt): 
    minus = np.array([[0,1,0], [0,-1,0], [1,0,0], [-1,0,0]])

    # Gets all data points, and transformed into (x,y)
    pos = []
    with open(opt.input, 'r') as file:
        for line in file.readlines():
            r, theta = map(lambda x: float(x), line[:-1].split(','))
            pos.append([ int(opt.scale * r * math.cos(toPhi(theta))),
                        int(-opt.scale * r * math.sin(toPhi(theta))) ])

    pos = np.asarray(pos)
    minimum = -np.min(pos)
    pos = pos - np.min(pos)
    # pos = np.apply_along_axis(lambda l: np.append(l, opt.duplicate), 1, pos)
    ans = np.copy(pos)
    if SHIFT:
        for i in range(minus.shape[0]):
            ans = np.concatenate((ans, np.apply_along_axis(lambda l: l - minus[i], 1, pos)))
    print (ans.shape)

    hm = HeatMap(ans.tolist())

    # ------------ Draw all points ------------
    hm.clickmap(save_as=opt.input + "_hit.png")

    img = hm.heatmap()
    
    draw = ImageDraw.Draw(img) 

    unit = 5
    font = ImageFont.truetype("/Library/Fonts/Arial.ttf", size=40)
    for i in range(5):
        radius = unit * i * opt.scale
        draw.ellipse((minimum - radius, minimum - radius, 
                      minimum + radius, minimum + radius), outline='black')
        draw.text(toxy((minimum, minimum), radius, 130), "%d\u00B0" % (unit * i), 'black', font=font)

    halfline = 5 * unit * opt.scale
    draw.line([(minimum - halfline, minimum), (minimum + halfline, minimum)], fill='black')
    draw.line([(minimum, minimum - halfline), (minimum, minimum + halfline)], fill='black')

    img.save(opt.input + "_heat.png")

    print ("Two files generated!")

if __name__ == '__main__':
    opt = parse_args()
    main(opt)
