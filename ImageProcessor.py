import cv2
import os
import time
import numpy as np


def _conv_img_to_gray(image: np.array) -> np.array:
    """
    Convert the given image to gray scale

    :param image: cv2 image or a numpy array
    :return: gray scaled image as np array
    """
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray_image


def _scale_image(image: np.array, dim: (int, int) = (175, 50)) -> np.array:
    """
    Resize the given image to the given dimensions, with cv2.INTER_AREA

    :param image: cv2 image
    :param dim: the target dimensions
    :return: cv2 image
    """
    resized_image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    return resized_image


def _detect_edges(image: np.array) -> np.array:
    """
    Detects the edges of an Images, by automatically calculation a threshold, blurring the image
    and using the threshold for the cv2.Canny function.

    :param image: cv2 image where you want the edges to be detected
    :return: the inverted mask of the detected edges as cv3 image
    """
    high_thresh, thresh_im = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    low_thresh = 0.5 * high_thresh
    blurred = cv2.GaussianBlur(image, (1, 1), 0)
    canny_edges = cv2.Canny(blurred, low_thresh, high_thresh)
    ret, mask = cv2.threshold(canny_edges, 0, 255, cv2.THRESH_BINARY_INV)
    return mask


def preprocess_image(image: np.array, width: int, height: int, tmp_file_location: str, file_name: str) -> None:
    """
    Processes the given image to an SVG file

    :param image: cv2 image you want to make to a svg
    :param width: width of the created svg
    :param height: height of the created svg
    :param tmp_file_location: location for the bitmap and the svg result
    :param file_name: name for the new file
    :return: None
    """
    gray = _conv_img_to_gray(image)
    edges = _detect_edges(gray)
    svg_path = os.path.join(tmp_file_location, "svg", f"{file_name}.svg")
    bmp_path = os.path.join(tmp_file_location, "bmp", f"{file_name}.bmp")
    cv2.imwrite(bmp_path, edges)
    os.system(f"rm {svg_path}")
    os.system(f"potrace"
              f" -b svg"
              f" --flat"
              f" --group"
              f" --width {width - 30}pt"
              f" --height {height - 30}pt"
              f" -o {svg_path} {bmp_path}")
    time.sleep(2)


def main():
    """
    To run in the main section

    :return: None
    """

    def test_drawing():
        """
        to test the conversion from an image to an SVG

        :return: None
        """
        image = cv2.imread("data/images/jpg_png/YiDiplom.png")
        preprocess_image(image, 1920, 1080, "data/images/", 'test')

    test_drawing()


if __name__ == "__main__":
    main()
