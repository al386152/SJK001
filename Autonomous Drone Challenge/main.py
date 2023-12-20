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
FORMA_IMAGEN = (240, 320) #, 3) # Obtenida de forma euristica

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


def datos_normalizados(l):
    minim = min(l)
    maxim = max(l)
    dif = maxim - minim

    return [(2 * ((v - minim) / dif) - 1) for v in l]

def ir_al_naufrago(pos):
    pass

print_state()
despega()
# Primero vamos al sitio
while not is_in_position(X_RESCATE, Y_RESCATE, ALTURA_VUELO):
    mostrar_imagen_ventral_como_yo_quiero()
    moverse_a_la_zona_del_rescate()
    print_state()

pos_momento_captura = HAL.get_position()
img, mask = mostrar_imagen_ventral_como_yo_quiero()
print(get_posiciones_naufragos(mask))
x, y, z, yaw = pos_momento_captura

while not is_in_position(x + 1, y, z, error=0):
    mover_posicion_respecto_barco(x + 1, y, z, 0)
    print_state()
img, mask = mostrar_imagen_ventral_como_yo_quiero()
print(get_posiciones_naufragos(mask))



# Luego, no paramos de buscar los naufragos hasta que no los hayamos encontrado todos

#dict_naufragos = dict()
#num_rescatados = 0
#while num_rescatados < NUM_NAUFRAGOS:
#    img, mask = mostrar_imagen_ventral_como_yo_quiero()
#    pos = get_posiciones_naufragos(mask)
    # Como no sé bien cómo transormar de píxeles a metros teniendo en cuenta la perspectiva
    #  El plan es que se mueva en una dirección hasta que esté justo encima.




