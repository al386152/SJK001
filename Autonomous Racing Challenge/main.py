from GUI import GUI
from HAL import HAL
# Enter sequential code!


import cv2
import time


def get_mask(min_range=(0, 125, 125), max_range=(30, 255, 255)):
    img = HAL.getImage()

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    red_mask = cv2.inRange(hsv, min_range, max_range)
    return red_mask

# TODO: falla aquí cuando no detecta la línea en, por ejemplo, las curvas
#   IndexError: tuple index out of range.
def get_momentums(red_mask):
    contours, _ = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return cv2.moments(contours[0])


def get_centroids(M):
    if M["m00"] != 0:
        cX = M["m10"] / M["m00"]
        cY = M["m01"] / M["m00"]
    else:
        cX, cY = 0, 0

    return cX, cY


# Estado de la lína (si está perdida, delante, etc.)
pos_centro = 320
velocidad_recta = 6


def get_velocidades(cX, cX_anterior, velocidad_anterior):
    # Si la línea está a la derecha vale más de 320
    # Si la línea está a la izquierda, vale menos de 320

    print(f"cX_anterior: {cX_anterior}, velocidad_anterior: {velocidad_anterior}")
    if cX == 0:
        # Estado: Línea perdida.
        print("Línea a la perdida")

        # Si se pierde la línea, gira hasta encontrarla otra vez.
        vel_lineal = 0
        # Si hemos perido la línea, gira en la dirección opuesta a la última posición conocida.
        vel_angular = -cX_anterior

    elif cX == pos_centro:
        # Estado: línea delante.
        vel_lineal = velocidad_recta
        vel_angular = 0
        print("Línea delante")
    else:
        # Estado: línea a los lados.
        # Si es una curva, lo mejor es frenar
        # TODO: Los siguientes valores deberían ser en función
        #vel_lineal = velocidad_anterior * 0.1
        vel_lineal = velocidad_recta #* (cX - cX_anterior)
        vel_angular = 0.01 * (cX_anterior - cX)
        if cX > pos_centro:
            # Estado: línea a la derecha
            print("Línea a la derecha")
        else:  # if cX < pos_centro:
            # Estado: línea a la izquierda
            print("Línea a la izquierda")

    print(f"vel_lineal: {vel_lineal}, vel_angular: {vel_angular}")
    return (vel_lineal, vel_angular)


i = 0
cX_anterior = pos_centro
vel = velocidad_recta
while True:
    red_mask = get_mask()
    cX, cY = get_centroids(get_momentums(red_mask))

    vel, rotacion = get_velocidades(cX, cX_anterior, vel)
    cX_anterior = cX

    HAL.setV(vel)
    HAL.setW(rotacion)

    GUI.showImage(red_mask)
    print('%d, cX: %.2f cY: %.2f' % (i, cX, cY))
    i += 1
