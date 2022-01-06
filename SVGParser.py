from xml.dom import minidom
import pyautogui
from svgpathtools import svg2paths2, Line as SVGLine, CubicBezier
from math import floor


def get_transform_from_svg(name):
    doc = minidom.parse(name)
    path_strings = [path.getAttribute('transform') for path in doc.getElementsByTagName('g') if
                    path.getAttribute('transform')]
    doc.unlink()
    translate, scale = None, None
    for t in path_strings[0].split():
        if str(t).startswith("translate"):
            w, h = t[10:-1].split(',')
            translate = float(w), float(h)
        elif str(t).startswith("scale"):
            w, h = t[6:-1].split(',')
            scale = float(w), float(h)
    return translate, scale


def calculate_offset(current_x, current_y, j):
    x, y = j.real, j.imag
    x_off, y_off = floor(x - current_x), floor(y - current_y)
    current_x, current_y = current_x + x_off, current_y + y_off
    return x_off, y_off, current_x, current_y


def scale_paths_iterator(name):
    translate, scale = get_transform_from_svg(f"data/images/svg/{name}.svg")
    paths, _, _ = svg2paths2(f"data/images/svg/{name}.svg")
    for path in paths:
        path = path.reversed()
        path = path.scaled(scale[0], scale[1])
        path = path.translated(complex(translate[0], translate[1]))
        yield path


def svg_to_action(name, action, current_x, current_y, path_length_range=(2, 100000), curve_steps=2):
    for path in scale_paths_iterator(name):
        if path_length_range[0] <= path.length() <= path_length_range[1]:
            x_off, y_off, current_x, current_y = calculate_offset(current_x, current_y, path[0].start)
            action.move_by_offset(x_off, y_off)
            action.click_and_hold()
            for element in path:
                if isinstance(element, SVGLine):
                    x_off, y_off, current_x, current_y = calculate_offset(current_x, current_y, element.start)
                    action.move_by_offset(x_off, y_off)
                    x_off, y_off, current_x, current_y = calculate_offset(current_x, current_y, element.end)
                    action.move_by_offset(x_off, y_off)
                elif isinstance(element, CubicBezier):
                    for i in range(curve_steps):
                        x_off, y_off, current_x, current_y = calculate_offset(current_x, current_y,
                                                                              element.point(i / curve_steps))
                        action.move_by_offset(x_off, y_off)
        action.release()


def svg_to_pyautogui(name, path_length_range=(2, 100000), curve_steps=2):
    for path in scale_paths_iterator(name):
        if path_length_range[0] <= path.length() <= path_length_range[1]:
            pyautogui.moveTo(path[0].start.real, path[0].start.imag)
            pyautogui.mouseDown()
            for element in path:
                if isinstance(element, SVGLine):
                    pyautogui.moveTo(element.start.real, element.start.imag)
                    pyautogui.moveTo(element.end.real, element.end.imag)
                elif isinstance(element, CubicBezier):
                    for i in range(curve_steps):
                        step = element.point(i / curve_steps)
                        pyautogui.moveTo(step.real, step.imag)
        pyautogui.mouseUp()


if __name__ == "__main__":
    pyautogui.PAUSE = 0.0000000001
    pyautogui.MINIMUM_SLEEP = 0.0
    svg_to_pyautogui("processed_image", curve_steps=50)
