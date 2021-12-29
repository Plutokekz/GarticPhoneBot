# Image to Gray Scale
# Gray image to edges
# Edges to SVG
# SVG to drawable lines
from pprint import pprint
import cv2
import os
from svgpathtools import svg2paths2, wsvg
import numpy as np
import time
from xml.dom import minidom


def _conv_img_to_gray(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray_image


def _scale_image(image, dim=(175, 50)):
    resized_image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    return resized_image


def _detect_edges(image):
    img_gray_blur = cv2.GaussianBlur(image, (5, 5), 0)
    canny_edges = cv2.Canny(img_gray_blur, 10, 70)
    ret, mask = cv2.threshold(canny_edges, 0, 255, cv2.THRESH_BINARY_INV)
    return mask


def parse_svg(name):
    doc = minidom.parse(name)  # parseString also exists
    path_strings = [path.getAttribute('d') for path in doc.getElementsByTagName('path')]
    doc.unlink()
    # M7807 343 c-4 -3 -7 -19 -7 -35 0 -33 -17 -38 -23 -5 -4 19 -4 18 -6 -5 -1 -22 4 -28 19 -28 15 0 20 7 20 30 0 17 7 33 18 39 14 9 15 10 1 11 -9 0 -19 -3 -22 -7z'
    return path_strings


def preprocess_image(image, steps=10, width=1516, height=848):
    s = np.linspace(0, 1, steps)
    grey = _conv_img_to_gray(image)
    edges = _detect_edges(grey)
    # scaled = _scale_image(edges, (width, height))
    cv2.imwrite("image.bmp", edges)
    os.system("rm image.svg")
    os.system("potrace -b svg --flat --group image.bmp")
    time.sleep(2)
    # paths, attributes = svg2paths("image.svg")
    paths, attributes, svg_attributes = svg2paths2("image.svg")
    w = int(svg_attributes['width'].split('.')[0])
    h = int(svg_attributes['height'].split('.')[0])

    if w >= width:
        s_w = width/w
    else:
        s_w = w/width
    if h >= height:
        s_h = height/h
    else:
        s_h = h/height

    print(f"scaling factors {s_w}, {s_h}")
    paths = [x.scaled(s_w, s_h) for x in paths]
    wsvg(paths, colors=None, filename="scaled.svg")
    print(svg_attributes)
    points = []
    for path in paths:
        for curve in path:
            points.append([(x.imag, x.real) for x in curve.points(s)])
    pprint(points)
    return points


def test_drawing():
    # curve_steps = np.linspace(0, 1, 50)
    # delay = 1/curve_steps
    image = cv2.imread("img.png")
    preprocess_image(image)
    # time.sleep(2)
    # print(preprocess_image(image))


if __name__ == "__main__":
    print(parse_svg("image.svg"))
