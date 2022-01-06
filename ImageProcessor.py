import cv2
import os
import time


def _conv_img_to_gray(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray_image


def _scale_image(image, dim=(175, 50)):
    resized_image = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)
    return resized_image


def _detect_edges(image):
    high_thresh, thresh_im = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    low_thresh = 0.5 * high_thresh
    blurred = cv2.resize(cv2.GaussianBlur(image, (35, 35), 0), (800, 600))
    canny_edges = cv2.Canny(blurred, low_thresh, high_thresh)
    ret, mask = cv2.threshold(canny_edges, 0, 255, cv2.THRESH_BINARY_INV)
    return mask


def preprocess_image(image, width, height, name):
    gray = _conv_img_to_gray(image)
    edges = _detect_edges(gray)
    cv2.imwrite(f"data/images/bmp/{name}.bmp", edges)
    os.system(f"rm {name}.svg")
    os.system(
        f"potrace -b svg --flat --group --width {width - 30}pt --height {height - 30}pt -o data/images/svg/{name}.svg data/images/bmp/{name}.bmp")
    time.sleep(2)


def test_drawing():
    image = cv2.imread("data/images/jpg_png/img.png")
    preprocess_image(image, 1920, 1080, 'test')


if __name__ == "__main__":
    test_drawing()
