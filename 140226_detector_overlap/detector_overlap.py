"""Determine area overlap/miss between a fixed square and rotating rectangle

For Groundparticle simulations
How much area overlap is there between a fixed square with surface .5 m^2
and a rectangle with sides 1m by 0.5m with same origin but rotated.

"""

import math

from random import uniform

import numpy as np

from matplotlib import pyplot as plt

from pointrect import Point, Rect


def run():
    square_size = (math.sqrt(2) / 2.) / 2.
    detector_long = 1. / 2.
    detector_short = 0.5 / 2.
    square = Rect(Point(-square_size, -square_size),
                  Point(square_size, square_size))

    angles = np.linspace(0, np.pi / 2., 50)
    overlap = []
    n = 200000

    for i, angle in enumerate(angles):
        plt.figure()
        xin = []
        xout = []
        yin = []
        yout = []
        count = 0
        for _ in range(n):
            long = uniform(-detector_long, detector_long)
            short = uniform(-detector_short, detector_short)
            point = Point(int, short).rotate(angle)
            if square.contains(point):
                xin.append(point.x)
                yin.append(point.y)
                count += 1
            else:
                xout.append(point.x)
                yout.append(point.y)
        overlap.append(count / (2. * n))
        plt.text(.4, .6, ('Angle: %.2f deg\nOverlap: %.3f m**2' %
                          (np.degrees(angle), overlap[-1])), ha='left')
        plt.scatter(xin, yin, s=2, c='black')
        plt.scatter(xout, yout, s=2, c='r')
        plt.plot([-square_size, -square_size, square_size, square_size, -square_size],
                 [-square_size, square_size, square_size, -square_size, -square_size])
        plt.xlabel('x (m)')
        plt.xlabel('y (m)')
        plt.title('Overlap between straight square and rotated rectangle')
        plt.axis('equal')
        plt.xlim(-1, 1)
        plt.ylim(-1, 1)
        plt.savefig('plots/rotated_%d.png' % i)
    plt.figure()
    plt.plot(angles, overlap)
    plt.show()


if __name__ == "__main__":
    run()
