from GUI import GUI
from HAL import HAL
# Enter sequential code!

import cv2
import time
import math


# Constantes:
NUM_NAUFRAGOS = 6
ALTURA_VUELO = 25
ALTURA_RAS_DEL_AGUA = 2
ALTURA_SEGUNDA_FOTO = 5
X_RESCATE = 35
Y_RESCATE = -35
# Obtenida de forma euristica (imagen.shape)
ANCHURA_IMAGEN = 320
ALTURA_IMAGEN = 240

POS_CENTRO_X = ANCHURA_IMAGEN / 2
POS_CENTRO_Y = ALTURA_IMAGEN / 2

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

def get_momentums(mask):
    try:
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        return cv2.moments(contours[0])
    except:
        return None

def get_centroids(M):
    cX, cY = 0, 0

    if M and M["m00"] != 0:
        cX = M["m10"] / M["m00"]
        cY = M["m01"] / M["m00"]

    return cX, cY


def centrarse_en_naufrago():
    error_x = -1
    error_y = -1
    while error_x == 0:
        print("centrarse_en_naufrago - EJE X")
        _, mask = mostrar_imagen_ventral_como_yo_quiero()
        cX, cY = get_centroids(get_momentums(mask))
        error_x = POS_CENTRO_X - cX
        moverse_en_cierta_direccion(error_x)
        print_state()

    while error_y == 0:
        _, mask = mostrar_imagen_ventral_como_yo_quiero()
        print("centrarse_en_naufrago - EJE Y")
        print_state()
        cX, cY = get_centroids(get_momentums(mask))
        error_y = POS_CENTRO_Y - cY
        moverse_en_cierta_direccion(error_y)

def moverse_a_la_zona_del_rescate():
    # Posición obtenida de forma heurística
    mover_posicion_respecto_barco(X_RESCATE, Y_RESCATE, ALTURA_VUELO, 0)

def moverse_en_cierta_direccion(vx=None, vy=None, vz=None, vyaw=None):
    # Prefiero poner los valores en funciones de [-1,1]

    x = vx if (vx is not None) else 0
    y = vy if (vy is not None) else 0
    z = vz if (vz is not None) else 0
    yaw = vyaw if (vyaw is not None) else 0

    HAL.set_cmd_vel(x, y, z, yaw)

def check(pos_a, pos_b, error = 0.5):
    return abs(pos_a - pos_b) < error

def is_in_position(x, y, z, error=0.5):
    pos_x, pos_y, pos_z = HAL.get_position()
    return (x is None or check(pos_x, x, error)) and (y is None or check(pos_y, y, error)) and (z is None or check(pos_z, z, error))

def is_in_the_correct_yaw(yaw, error = 0.5):
    return check(HAL.get_yaw(), yaw, error)

def reconocer_cara(src):
    # Si se reconoce la car
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)

    # Load pre-trained classifiers
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    # eyeCascade = cv2.CascadeClassifier('haarcascade_eye.xml')

    faces = list()
    # Detect faces
    try:
        faces = faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(0, 0))

        # for (x, y, w, h) in faces:
        # roi_gray = gray[y:y + h, x:x + w]
        # roi_src = src[y:y + h, x:x + w]

        # Draw rectangle around face
        # cv2.rectangle(src, (x, y), (x + w, y + h), (255, 0, 0), 2)
        # # Detect eyes in face ROI
        # eyes = eyeCascade.detectMultiScale(roi_gray)
        # for (ex, ey, ew, eh) in eyes:
        #     # Draw rectangle around eyes
        #     cv2.rectangle(roi_src, (ex, ey), (ex + ew, ey + eh), (0, 0, 255), 2)
    finally:
        return faces

def esperar(t):
    print(f"Esperando {t} segundos")
    time.sleep(t)
def parar():
    x, y, z = HAL.get_position()
    mover_posicion_respecto_barco(x, y, z, HAL.get_yaw())

def despega():
    HAL.takeoff(ALTURA_VUELO)

def print_state():
    print(f"get_position: {HAL.get_position()}")
    print(f"get_orientation: {HAL.get_orientation()}")
    print(f"get_roll: {HAL.get_roll()}")
    print(f"get_pitch: {HAL.get_pitch()}")
    print(f"get_yaw: {HAL.get_yaw()}")
    print(f"get_landed_state: {HAL.get_landed_state()}")
    print("-----")

def get_posiciones_naufragos(mask):
    print("Consiguiendo las posiciones de los naufragos")
    posiciones = list()
    for tup_centro_x_y, tup_width_height, angle in get_bounding_boxes(mask):
        x, y = tup_centro_x_y
        posiciones.append((x, y, angle))
    return posiciones

def mostrar_imagen_ventral_como_yo_quiero():
    ventral = get_ventral_image()
    mask = get_not_blue_mask(ventral)
    GUI.showImage(ventral)
    GUI.showLeftImage(mask)
    return ventral, mask

# Sacado un poco de internet
#principal_point_x, principal_point_y = (ANCHURA_IMAGEN / 2, ALTURA_IMAGEN / 2)
def pixels_to_cartesian(pixels, principal_point, depth = ALTURA_VUELO, focal_length = 500):
    cartesian = ((pixels - principal_point) / focal_length) * depth
    return cartesian

def _pixels_a_coordenadas_aprox(posiciones, pos_momento_captura = HAL.get_position()):

    coordenadas = list()
    pos_x, pos_y, _ = pos_momento_captura
    for x, y, yaw in posiciones:
        x = pixels_to_cartesian(x, ANCHURA_IMAGEN / 2)
        y = pixels_to_cartesian(y, ALTURA_IMAGEN / 2)
        coordenadas.append( (pos_x + x, pos_y + y, math.degrees(yaw) ) )
    return coordenadas

def pixels_a_coordenadas_aprox(posiciones, difs_perspectiva, pos_momento_captura = HAL.get_position()):

    dif_x, dif_y = difs_perspectiva
    print(f"dif_x: {dif_x}, dif_y: {dif_y}")
    coordenadas = list()
    pos_x, pos_y, _ = pos_momento_captura
    for x, y, yaw in posiciones:
        x = x / dif_x
        y = y / dif_y
        print(f" x: {x}, y: {y}, yaw: {yaw}")
        coordenadas.append((pos_x + x, pos_y + y, math.radians(yaw)))
        print(f"coordenadas: {coordenadas} ")
    return coordenadas


def ir_al_naufrago(pos, difs_perspectiva):
    while not is_in_position(POS_CENTRO_X, POS_CENTRO_Y, ALTURA_SEGUNDA_FOTO):
        x, y, yaw = pos
        # Nos movemos a ras del agua
        while not is_in_position(x, y, ALTURA_SEGUNDA_FOTO):
            mostrar_imagen_ventral_como_yo_quiero()
            mover_posicion_respecto_barco(x, y, ALTURA_SEGUNDA_FOTO, 0)
            print_state()
            print("Yendo al náufrago")

        esperar(10)
        pos = pixels_a_coordenadas_aprox(get_posiciones_naufragos(mask), difs_perspectiva)

def ir_al_otro_extremo_del_naufrago():
    im, mask = mostrar_imagen_ventral_como_yo_quiero()
    cara = reconocer_cara(im)
    vx, vy, _ = HAL.get_velocity()
    while len(cara) == 0:
        print(f"Yendo al otro extremo del naufrago | vx: {vx}, vy: {vy} ")
        moverse_en_cierta_direccion(vx=vx, vy=vy, vz=None, vyaw=None)
        print_state()
        cara = reconocer_cara(im)
    parar()
    return cara

def test_movimiento():
    mostrar_imagen_ventral_como_yo_quiero()
    mover_posicion_respecto_barco(15, -15, 5, 0)
    print(f"test: {HAL.get_position()}")
    esperar(5)


    while not is_in_position(X_RESCATE, Y_RESCATE, ALTURA_VUELO, error=1):
        print("test")
        mostrar_imagen_ventral_como_yo_quiero()
        moverse_en_cierta_direccion(vx=2, vy=-2, vz=0.5, vyaw=None)
        print(f"test: {HAL.get_position()}")

def obtencion_diferencias():
    # Como no he encontrado una buena forma de pasar de los píxels de la imagen a metros
    #   (no tengo cosas como la distancia focal para poder hacer bien el cambio),
    #   he tomado la decisión de que, primero calcula cuanto es a partir de la diferencia y luego rescata.

    print_state()
    while not is_in_position(0, 0, ALTURA_VUELO, error=0.1):
        print("TEST - PERSPECTIVA 0")
        print_state()
        _, mask = mostrar_imagen_ventral_como_yo_quiero()
        mover_posicion_respecto_barco(0, 0, ALTURA_VUELO, 0)
    _, mask = mostrar_imagen_ventral_como_yo_quiero()
    pos = get_posiciones_naufragos(mask)[0]
    while not is_in_position(1, 0, ALTURA_VUELO, error=0.1):
        print("TEST - PERSPECTIVA 1")
        print_state()
        _, mask = mostrar_imagen_ventral_como_yo_quiero()
        mover_posicion_respecto_barco(1, 0, ALTURA_VUELO, 0)
    _, mask = mostrar_imagen_ventral_como_yo_quiero()
    pos2 = get_posiciones_naufragos(mask)[0]

    print(f"pos: {pos}")
    print(f"pos2:{pos2}")
    x1, y1, a1 = pos
    x2, y2, a2 = pos2
    dif_x = x2 - x1
    dif_y = y2 - y1
    dif_a = a2 - a1
    print(f"dif: ({dif_x}, {dif_y}, {dif_a},) ")

    #return (dif_x, dif_y, dif_a)
    #return (round(dif_x), round(dif_y), round(dif_a))
    return (x2, y2)

print_state()
despega()
difs_perspectiva = obtencion_diferencias()

# Primero vamos al sitio
while not is_in_position(X_RESCATE, Y_RESCATE, ALTURA_VUELO):
    mostrar_imagen_ventral_como_yo_quiero()
    moverse_a_la_zona_del_rescate()
    print_state()
    print("-- Yendo a la zona del naufragio --")

print("-- Zona del naufragio alcanzada --")
pos_momento_captura = HAL.get_position()
img, mask = mostrar_imagen_ventral_como_yo_quiero()
# Desde esta posición, podemos ver todos los naufragos (si no, habría que hacer un poco más de exploración).
posiciones_naufragos = pixels_a_coordenadas_aprox(get_posiciones_naufragos(mask), difs_perspectiva, pos_momento_captura)

print("Recogiendo a los naufragos")
naufragos = dict()
i = 0
while len(naufragos) < NUM_NAUFRAGOS:
    print(f"Naufragos recogidos: {len(naufragos)}/{NUM_NAUFRAGOS}")
    pos = posiciones_naufragos[i]
    ir_al_naufrago(pos, difs_perspectiva)
    im, mask = mostrar_imagen_ventral_como_yo_quiero()
    cara = reconocer_cara(im)
    if len(cara) != 0:
        print("Cara reconocida")
        # if cara not in naufragos: # Por como lo estamos haciendo, no debería repetirse.
        naufragos[pos] = cara
        i += 1
    else:
        print("Cara no reconocida")
        # No se si así la idea es buena
        naufragos[pos] = ir_al_otro_extremo_del_naufrago()
        i += 1


# Creo que es necesario meter un "while True"
while True:
    mostrar_imagen_ventral_como_yo_quiero()
