from GUI import GUI
from HAL import HAL
# Enter sequential code!

import cv2
import time

# Constantes:
NUM_NAUFRAGOS = 6
ALTURA_VUELO = 25
X_RESCATE = 35
Y_RESCATE = -35

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

def get_not_blue_mask(img):
    return ~get_blue_mask(img)

def get_bounding_boxes(mask):
    try:
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        return [cv2.minAreaRect(contour) for contour in contours]
    except:
        return None

def mover_posicion_respecto_barco(x, y, z, yaw):
    HAL.set_cmd_pos(x, y, z, yaw)

def moverse_a_la_zona_del_rescate():
    # Posición obtenida de forma heurística
    mover_posicion_respecto_barco(X_RESCATE, Y_RESCATE, ALTURA_VUELO, 0)

def check(pos_a, pos_b, error = 0.5):
    return abs(pos_a - pos_b) < error

def is_in_position(x, y, z, error=0.5):
    pos_x, pos_y, pos_z = HAL.get_position()
    return (x is None or check(pos_x, x, error)) and (y is None or check(pos_y, y, error)) and (z is None or check(pos_z, z, error))

def establecer_velocidad(x = 0, y = 0, z = 0):
    HAL.set_cmd_vel(x, y, z, 0)

def hay_naufrago():
    return False

def reconocer_cara(src):
    # Si se reconoce la car
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)

    # Load pre-trained classifiers
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    #eyeCascade = cv2.CascadeClassifier('haarcascade_eye.xml')

    # Detect faces
    faces = faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(0, 0))

    # for (x, y, w, h) in faces:
        #roi_gray = gray[y:y + h, x:x + w]
        #roi_src = src[y:y + h, x:x + w]

        # Draw rectangle around face
        # cv2.rectangle(src, (x, y), (x + w, y + h), (255, 0, 0), 2)
        # # Detect eyes in face ROI
        # eyes = eyeCascade.detectMultiScale(roi_gray)
        # for (ex, ey, ew, eh) in eyes:
        #     # Draw rectangle around eyes
        #     cv2.rectangle(roi_src, (ex, ey), (ex + ew, ey + eh), (0, 0, 255), 2)
    return faces

# Esto es para tener un esquema.
def avanzar_hasta_posicion_y_comprobacion(x, y, paso = 1):
    while not is_in_position(x, y, None):
        establecer_velocidad(x=paso * (not x is None), y=paso * (not y is None))
        imagen = mostrar_imagen_ventral_como_yo_quiero()
        if hay_naufrago():
            parar()
            caras = reconocer_cara(imagen)
            if len(caras) != 0:
                return caras_naufragos.add(caras[0])

def vueltas_en_cuadrados(avanze = 1, pseudo_radio = 1, pos_actual = HAL.get_position()):
    x, y, z = pos_actual
    # La idea es, avanzamos un poco, damos una vuelta, avanzamos otro poco, damos otra vuelta
    mover_posicion_respecto_barco(x, y + avanze, z, 0)
    mover_posicion_respecto_barco(x, y + pseudo_radio, z, 0)

def esperar(t):
    time.sleep(t)


def parar():
    HAL.set_cmd_vel(0, 0, 0, 0)


def despega():
    HAL.takeoff(10)


def print_state():
    print(f"get_position: {HAL.get_position()}")
    # Parece que no va bien la siguiente función, al menos al iniciar:
    # print(f"get_velocity: {HAL.get_velocity()}")
    # Parece que no va bien la siguiente función, al menos al iniciar:
    # print(f"get_yaw_rate: {HAL.get_yaw_rate()}")
    print(f"get_orientation: {HAL.get_orientation()}")
    print(f"get_roll: {HAL.get_roll()}")
    print(f"get_pitch: {HAL.get_pitch()}")
    print(f"get_yaw: {HAL.get_yaw()}")
    print(f"get_landed_state: {HAL.get_landed_state()}")
    print("-----")

def mostrar_imagen_ventral_como_yo_quiero():
    ventral = get_ventral_image()
    mask = get_not_blue_mask(ventral)
    GUI.showImage(ventral)
    GUI.showLeftImage(mask)
    return ventral, mask


print_state()
despega()

while not is_in_position(X_RESCATE, Y_RESCATE, ALTURA_VUELO):
    # frontal = get_frontal_image()
    mostrar_imagen_ventral_como_yo_quiero()

    moverse_a_la_zona_del_rescate()
    print_state()

while True:
    img, mask = mostrar_imagen_ventral_como_yo_quiero()
    print(get_bounding_boxes(mask))
    esperar(5)

caras_naufragos = set()
num_rescatados = 0
#while num_rescatados < NUM_NAUFRAGOS:


