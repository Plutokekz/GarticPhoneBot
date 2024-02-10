"""
This module contains the functions to convert an image to an SVG file
"""

import time
import xml.dom.minidom
from typing import Generator, Tuple
import math

import pyautogui
import svgpathtools
import selenium.webdriver
from svgpathtools import Line


def get_transform_from_svg(file_name: str) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """
    Reads the transform attribute from the given svg file

    :param file_name: path to the svg file
    :return: (translate, scale)
    """
    doc = xml.dom.minidom.parse(file_name)
    path_strings = [
        path.getAttribute("transform") for path in doc.getElementsByTagName("g") if path.getAttribute("transform")
    ]
    doc.unlink()
    translate, scale = None, None
    for t in path_strings[0].split():
        if str(t).startswith("translate"):
            w, h = t[10:-1].split(",")
            translate = float(w), float(h)
        elif str(t).startswith("scale"):
            w, h = t[6:-1].split(",")
            scale = float(w), float(h)
    if translate is None:
        translate = 0, 0
    if scale is None:
        scale = 1, 1
    return translate, scale


def perpendicular_distance(pt, line: Line) -> float:
    """Calculate the perpendicular distance between a point and a line."""
    return float(
        abs(
            (line.end.imag - line.start.imag) * pt.real
            - (line.end.real - line.start.real) * pt.imag
            + line.end.real * line.start.imag
            - line.end.imag * line.start.real
        )
        / ((line.end.imag - line.start.imag) ** 2 + (line.end.real - line.start.real) ** 2) ** 0.5
    )


def douglas_peucker(path: svgpathtools.Path, epsilon: float) -> svgpathtools.Path:
    """Simplify a polyline using the Douglas-Peucker algorithm."""
    dmax = 0.0
    index = 0
    end = len(path)
    if end < 3:
        return path
    for i in range(1, end - 1):
        d = perpendicular_distance(path[i], Line(path[0], path[end - 1]))
        if d > dmax:
            index = i
            dmax = d

    if dmax > epsilon:
        rec_results1 = douglas_peucker(path[: index + 1], epsilon)
        rec_results2 = douglas_peucker(path[index:], epsilon)
        result_list = rec_results1[:-1] + rec_results2
    else:
        result_list = [path[0], path[end - 1]]
    return result_list


def calculate_offset(current_x: int, current_y: int, j: complex) -> Tuple[int, int, int, int]:
    """
    Calculates the offset from the current x,y and the new x,y

    :param current_x: The current x position
    :param current_y: the current y position
    :param j: the new x and y position a complex number where the real part is x and the imaginary part is y
    :return: (x_offset, y_offset, current_x, current_y)
    """
    x, y = j.real, j.imag
    x_off, y_off = math.floor(x - current_x), math.floor(y - current_y)
    current_x, current_y = current_x + x_off, current_y + y_off
    return x_off, y_off, current_x, current_y


def scale_paths_generator(file_name: str) -> Generator[svgpathtools.Path, None, None]:
    """
    Gets the Transformation from the svg file and applies it to all the Path's in it

    :param file_name: String to the svg file
    :return: yields every transformed Path in the svg file
    """
    translate, scale = get_transform_from_svg(file_name)
    paths, _, _ = svgpathtools.svg2paths2(file_name)
    for path in paths:
        path = path.reversed()
        path = path.scaled(scale[0], scale[1])
        path = path.translated(complex(translate[0], translate[1]))
        yield path


def svg_to_action(
    action: selenium.webdriver.ActionChains,
    current_x: int,
    current_y: int,
    file_name: str = "app/data/images/svg/processed_image.svg",
    path_length_range: Tuple[int, int] = (2, 100000),
    curve_steps: int = 2,
) -> None:
    """
    Parses the svg file to a Selenium ActionChain

    :param current_x:
    :param curve_steps:
    :param file_name:
    :param path_length_range:
    :param action: ActionChain Object from Selenium :param current_x: the current x from the courser in Selenium
    :param current_y: the current y from the courser in Selenium :param file_name: file name for the svg file you
    want to parse :param path_length_range: defines the minimum and maximum length for a path to get drawn :param
    curve_steps: the number of steps for the CubicBezier Curves you want to make (more steps = smother curves -> also
    needs more time to draw) :return: None
    """
    for path in scale_paths_generator(file_name):
        if path_length_range[0] <= path.length() <= path_length_range[1]:
            # path = douglas_peucker(path, 0.5)
            x_off, y_off, current_x, current_y = calculate_offset(current_x, current_y, path[0].start)
            action.move_by_offset(x_off, y_off)
            action.click_and_hold()
            for element in path:
                if isinstance(element, svgpathtools.Line):
                    x_off, y_off, current_x, current_y = calculate_offset(current_x, current_y, element.start)
                    action.move_by_offset(x_off, y_off)
                    x_off, y_off, current_x, current_y = calculate_offset(current_x, current_y, element.end)
                    action.move_by_offset(x_off, y_off)
                elif isinstance(element, svgpathtools.CubicBezier):
                    for i in range(curve_steps):
                        x_off, y_off, current_x, current_y = calculate_offset(
                            current_x, current_y, element.point(i / curve_steps)
                        )
                        action.move_by_offset(x_off, y_off)
        action.release()


def svg_to_pyautogui(
    file_name: str = "data/images/svg/processed_image.svg",
    path_length_range: Tuple[int, int] = (2, 100000),
    curve_steps: int = 2,
    off_set=500,
) -> None:
    """
    Parses the given svg file to pyautogui mouse movement and clicks, which get executed immediately
    :param file_name: the svg file you want to parse
    :param path_length_range: defines the minimum and maximum length for a path to get drawn
    :param curve_steps: the number of steps for the CubicBezier Curves you want to make (more steps = smother curves ->
    also needs more time to draw)
    :return: None
    """
    for path in scale_paths_generator(file_name):
        if path_length_range[0] <= path.length() <= path_length_range[1]:
            pyautogui.moveTo(path[0].start.real + off_set, path[0].start.imag + off_set)
            pyautogui.mouseDown()
            for element in path:
                if isinstance(element, svgpathtools.Line):
                    pyautogui.moveTo(element.start.real + off_set, element.start.imag + off_set)
                    pyautogui.moveTo(element.end.real + off_set, element.end.imag + off_set)
                elif isinstance(element, svgpathtools.CubicBezier):
                    for i in range(curve_steps):
                        step = element.point(i / curve_steps)
                        pyautogui.moveTo(step.real + off_set, step.imag + off_set)
        pyautogui.mouseUp()


def main() -> None:
    """
    To trigger the failsafe press <STRG+ALT+ENTF>
    To test the svgparser run the pyautogui version with very small pauses and sleep times to see fast results
    be aware to have some drawing program at the right position open, to see some results and not getting the
    desktop dragged around. You have 5 seconds after starting to stop the program before it start drawing.
    To trigger the failsafe press <STRG+ALT+ENTF>

    :return: None
    """
    time.sleep(5)
    pyautogui.PAUSE = 0.0000000001
    # pyautogui.MINIMUM_SLEEP = 0.0
    svg_to_pyautogui(curve_steps=3)


if __name__ == "__main__":
    main()
