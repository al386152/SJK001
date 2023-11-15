from GUI import GUI
from HAL import HAL
# Enter sequential code!

import cv2
import time

# Constantes:
pos_centro = 320
velocidad_recta = 6  # Parece que con 25 sería posible
# Este tiene mucho peso cuando los cambios son bruscos
# peso_constante = 0.0021
peso_constante = 0.005
# Este tiene mucho peso cuando los cambios son medios
# peso_derivada = 0.00045
peso_derivada = 0.0004
# Este tiene mucho peso cuando los cambios son leves
# peso_integral = 0.00003
peso_integral = 0.000004


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


def get_velocidades(cX, prev_error, acumulacion_error):
    # Si la línea está a la derecha vale más de 320
    # Si la línea está a la izquierda, vale menos de 320
    error = pos_centro - cX
    diff_error = prev_error - error
    if cX == 0:
        print("Línea perdida")
        # vel_angular = (-1 if error < 0 else 1)
        # vel_lineal = -1
        vel_angular = 0
        vel_lineal = 0
        # diff_error = 0
        # acumulacion_error = 0

    elif cX == pos_centro:  # error == 0
        # Estado: línea delante.
        vel_lineal = velocidad_recta
        vel_angular = 0
        acumulacion_error = 0
        print("Línea delante")
    else:
        acumulacion_error += error
        # Estado: línea a los lados.
        # Si es una curva, lo mejor es frenar
        vel_lineal = velocidad_recta  # * (1 - (abs(cX - pos_centro) / pos_centro))
        vel_angular = peso_constante * error + peso_derivada * diff_error + peso_integral * acumulacion_error
        if cX > pos_centro:
            # Estado: línea a la derecha
            print("Línea a la derecha")
        else:  # if cX < pos_centro:
            # Estado: línea a la izquierda
            print("Línea a la izquierda")

    print(f"vel_lineal: {vel_lineal}, vel_angular: {vel_angular}, acumulacion_error: {acumulacion_error}")
    return (vel_lineal, vel_angular, error, acumulacion_error)


def parar(t):
    HAL.setV(0)
    HAL.setW(0)

    time.sleep(t)


i = 0
rotacion = 0
error = 0
vel = velocidad_recta
acumulacion_error = 0
min_acumulacion = 0
max_acumulacion = 0
while True:
    red_mask = get_mask()
    cX, cY = get_centroids(get_momentums(red_mask))

    vel, rotacion, error, acumulacion_error = get_velocidades(cX, error, acumulacion_error)
    min_acumulacion = min(min_acumulacion, acumulacion_error)
    max_acumulacion = max(max_acumulacion, acumulacion_error)
    print(f"min_acumulacion: {min_acumulacion}, max_acumulacion: {max_acumulacion} ")

    HAL.setV(vel)
    HAL.setW(rotacion)

    GUI.showImage(red_mask)
    print('%d, cX: %.2f cY: %.2f' % (i, cX, cY))
    i += 1

    # if i % 20 == 0: parar(1)
