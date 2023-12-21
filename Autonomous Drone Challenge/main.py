from GUI import GUI
from HAL import HAL
# Enter sequential code!

import cv2
import time

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

def moverse_en_cierta_direccion(vx=None, vy=None, vz=None, vyaw=None):
    # Prefiero poner los valores en funciones de [-1,1]

    x = vx * (vx is not None)
    y = vy * (vy is not None)
    z = vz * (vz is not None)
    yaw = vyaw * (vyaw is not None)

    HAL.set_cmd_vel(x, y, z, yaw)

def check(pos_a, pos_b, error = 0.5):
    return abs(pos_a - pos_b) < error

def is_in_position(x, y, z, error=0.5):
    pos_x, pos_y, pos_z = HAL.get_position()
    return (x is None or check(pos_x, x, error)) and (y is None or check(pos_y, y, error)) and (z is None or check(pos_z, z, error))


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
    time.sleep(t)
def parar():
    HAL.set_cmd_vel(0, 0, 0, 0)
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

def pixels_a_coordenadas_aprox(posiciones, pos_momento_captura = HAL.get_position()):

    coordenadas = list()
    pos_x, pos_y, _ = pos_momento_captura
    for x, y, yaw in posiciones:
        x = pixels_to_cartesian(x, ANCHURA_IMAGEN / 2)
        y = pixels_to_cartesian(y, ALTURA_IMAGEN / 2)
        coordenadas.append( (pos_x + x, pos_y + y, yaw) )
    return coordenadas

def ir_al_naufrago(pos):
    x, y, yaw = pos
    # Nos movemos a ras del agua
    while not is_in_position(x, y, ALTURA_SEGUNDA_FOTO):
        mostrar_imagen_ventral_como_yo_quiero()
        mover_posicion_respecto_barco(x, y, ALTURA_SEGUNDA_FOTO, yaw)
        print_state()
        print("Yendo al náufrago")
    print("Corrigiendo la posición")
    # Tratamos de corregir la dirección
    parar()
    # Si detecta varias posiciones, a la que vamos será la más cercana
    _p = sorted(get_posiciones_naufragos(mask), key=lambda coord: (coord[0] ** 2 + coord[1] ** 2)**2)
    posiciones = pixels_a_coordenadas_aprox(_p)
    x, y, yaw = posiciones[0]
    while not is_in_position(x, y, ALTURA_RAS_DEL_AGUA):
        mostrar_imagen_ventral_como_yo_quiero()
        mover_posicion_respecto_barco(x, y, ALTURA_RAS_DEL_AGUA, yaw)
        print_state()
        print("Yendo al náufrago (dir. corregida)")

def ir_al_otro_extremo_del_naufrago():
    im, mask = mostrar_imagen_ventral_como_yo_quiero()
    cara = reconocer_cara(im)
    while len(cara) == 0:
        print("yendo al otro extremo del naufrago")
        print_state()
        cara = reconocer_cara(im)
    parar()
    return cara


print_state()
despega()
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
posiciones_naufragos = pixels_a_coordenadas_aprox(get_posiciones_naufragos(mask), pos_momento_captura)

print("Recogiendo a los naufragos")
naufragos = dict()
i = 0
while len(naufragos) < NUM_NAUFRAGOS:
    print(f"Naufragos recogidos: {len(naufragos)}/{NUM_NAUFRAGOS}")
    pos = posiciones_naufragos[i]
    ir_al_naufrago(pos)
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
