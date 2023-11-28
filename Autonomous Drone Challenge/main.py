from GUI import GUI
from HAL import HAL
# Enter sequential code!

import cv2
import time

# Constantes:
pos_barco = [0, 0, 0]


def get_frontal_image():
    return HAL.get_frontal_image()


def get_ventral_image():
    return HAL.get_ventral_image()


def get_mask(img=HAL.get_frontal_image(), min_range=(0, 125, 125), max_range=(30, 255, 255)):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, min_range, max_range)
    return mask


# https://i.stack.imgur.com/TSKh8.png
def get_green_mask(img):
    return get_mask(img, min_range=(36, 25, 25), max_range=(70, 255, 255))


def get_blue_mask(img):
    return get_mask(img, min_range=(85, 25, 140), max_range=(150, 255, 255))


def get_momentums(red_mask):
    try:
        contours, _ = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        return cv2.moments(contours[0])
    except:
        return None


def get_centroids(M):
    cX, cY = 0, 0

    if M and M["m00"] != 0:
        cX = M["m10"] / M["m00"]
        cY = M["m01"] / M["m00"]

    return cX, cY


def mover_posicion_respecto_barco(x, y, z, yaw):
    HAL.set_cmd_pos(x, y, z, yaw)


def parar(t):
    time.sleep(t)


def print_state():
    print(f"get_position: {HAL.get_position()}")
    print(f"get_velocity: {HAL.get_velocity()}")
    print(f"get_yaw_rate: {HAL.get_yaw_rate()}")
    print(f"get_orientation: {HAL.get_orientation()}")
    print(f"get_roll: {HAL.get_roll()}")
    print(f"get_pitch: {HAL.get_pitch()}")
    print(f"get_yaw: {HAL.get_yaw()}")
    print(f"get_landed_state: {HAL.get_landed_state()}")
    print("-----")


i = 0
while True:
    frontal = get_frontal_image()
    ventral = get_ventral_image()

    print_state()
    # HAL.takeoff(1)
    mover_posicion_respecto_barco(0, 0, 10, 0)
    # mover_posicion_respecto_barco(1, 2, 5, 0)

    # GUI.showImage(get_green_mask(frontal))
    GUI.showLeftImage(get_blue_mask(ventral))
    GUI.showImage(get_blue_mask(ventral))
    # GUI.showLeftImage(ventral)

