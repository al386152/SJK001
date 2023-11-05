from GUI import GUI
from HAL import HAL
# Enter sequential code!

   
import cv2
import time

def get_momentums():
  img = HAL.getImage()
   
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    red_mask = cv2.inRange(hsv,
                            (0, 125, 125),    
                            (30, 255, 255))
   
    contours, hierarchy = cv2.findContours(red_mask,
                                            cv2.RETR_TREE,
                                            cv2.CHAIN_APPROX_SIMPLE)
   
    return cv2.moments(contours[0])
 
  def get_centroids(M):
    if M["m00"] != 0:
      cX = M["m10"] / M["m00"]
      cY = M["m01"] / M["m00"]
    else:
      cX, cY = 0, 0
     
    return cX, cY


# Estado de la lína (si está perdida, delante, etc.)
ESTADO_PERDIDA    = -1
ESTADO_DELANTE    = 0
ESTADO_DERECHA    = 1
ESTADO_IZQUIERDA  = 2


i = 0
speed = 1
val = 320

estado = ESTADO_PERDIDA

while True:
   
    cX, cY = get_centroids(get_momentums())
   
    # Si la línea está a la derecha vale más de 320
      # Si la línea está a la izquierda, vale menos de 320  
     
    if cX > 0:
      err = val - cX
     
     
      #HAL.setV(speed)
      #HAL.setW(0.01 * err)
     
    GUI.showImage(red_mask)
    print('%d, cX: %.2f cY: %.2f' % (i, cX, cY) )
    i += 1


