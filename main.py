import cv2
import numpy as np
import pyautogui


def find_centroids(dst):
    ret, dst = cv2.threshold(dst, 0.01 * dst.max(), 255, 0)
    dst = np.uint8(dst)

    # find centroids
    ret, labels, stats, centroids = cv2.connectedComponentsWithStats(dst)
    # define the criteria to stop and refine the corners
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100,
                0.001)
    corners = cv2.cornerSubPix(gray, np.float32(centroids), (5, 5),
                               (-1, -1), criteria)
    return corners


image = cv2.imread("img.png")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

gray = np.float32(gray)

dst = cv2.cornerHarris(gray, 2, 3, 0.04)

dst = cv2.dilate(dst, None)
start = (5115, 586)
end = (7034, 1654)
# Threshold for an optimal value, it may vary depending on the image.
# image[dst > 0.01*dst.max()] = [0, 0, 255]

# Get coordinates
corners = find_centroids(dst)
# To draw the corners
pyautogui.moveTo(start)
pyautogui.click()
pyautogui.sleep(5)
pyautogui.mouseDown()
for corner in corners:
    print(corner)
    image[int(corner[1]), int(corner[0])] = [0, 0, 255]
    pyautogui.moveTo(start[0] + int(corner[1]), start[1] + int(corner[0]))
pyautogui.mouseUp()

cv2.imshow('dst', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
