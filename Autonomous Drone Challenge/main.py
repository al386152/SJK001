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


def get_mask(min_range=(0, 125, 125), max_range=(30, 255, 255)):
    img = HAL.getImage()

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    red_mask = cv2.inRange(hsv, min_range, max_range)
    return red_mask


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
    print(f"position: {HAL.get_position()}")
    print(f"velocity: {HAL.get_velocity()}")
    print(f"yaw_rate: {HAL.get_yaw_rate()}")
    print(f"orientation: {HAL.get_orientation()}")
    print(f"roll: {HAL.get_roll()}")
    print(f"pitch: {HAL.get_pitch()}")
    print(f"yaw: {HAL.get_yaw()}")
    print(f"landed_state: {HAL.get_landed_state()}")
    print("-----")


while True:
    frontal = get_frontal_image()
    ventral = get_ventral_image()

    print_state()
    mover_posicion_respecto_barco(-2, 2, 10, 0)

    GUI.showImage(frontal)
    GUI.showLeftImage(ventral)
    i += 1

    # if i % 20 == 0: parar(1)
