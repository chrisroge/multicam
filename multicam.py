import cv2
import time
from threading import Thread
from PIL import Image
import numpy as np
import itertools
import sys
import datetime

from matplotlib.image import _ImageBase

# custom modules
import VideoCapture


# 1920 x 1080
# 3 images wide = 640 x 480
# 2 images wide = 720 x 540
# only 2 images = 960 x 720

print("PRESS Q IN WINDOW TO QUIT...")

no_image = cv2.imread("no_image.png", cv2.IMREAD_COLOR)
userN = sys.argv[1]
passW = sys.argv[2]

# get list of cameras
with open('cameras.txt') as f:
    cameras = f.read().splitlines()
    


def build_grid(imgs, w, h):

    n = w*h    

    # assume all frames are same size
    img_h, img_w, img_c = imgs[0].shape

    m_x = 0
    m_y = 0 

    imgmatrix = np.zeros((img_h * h + m_y * (h - 1),
                          img_w * w + m_x * (w - 1),
                          img_c),
                         np.uint8)

    imgmatrix.fill(255)    

    positions = itertools.product(range(w), range(h))
    for (x_i, y_i), img in zip(positions, imgs):
        x = x_i * (img_w + m_x)
        y = y_i * (img_h + m_y)
        resize_image = cv2.resize(img, image_size, interpolation = cv2.INTER_AREA)
        imgmatrix[y:y+img_h, x:x+img_w, :] = resize_image


    return imgmatrix



time.sleep(60)  # give crappy reolink camera rtmp servers time to recover


streams = []


for camera in cameras:
    streams.append(VideoCapture.VideoCapture("rtsp://" + userN + ":" + passW + "@" + camera + ":554/h264Preview_01_main"))


# infinite loop
while True:
    
    imgs = []

    for stream in streams:
        imgs.append(VideoCapture.GetLatestFrame._frame(stream))


    
    for img in imgs:
        if img is None:
            print("Image is None!")
            break

    

    image_count = len(imgs)


    if image_count > 4:
        w = 3
        h = 2
        # resize to 640 x 480
        image_size = (640, 480)        
        no_image = cv2.resize(no_image, image_size, interpolation = cv2.INTER_AREA)

    if image_count <= 4:
        w = 2
        h = 2 
        # resize to 960
        image_size = (720, 540)
        no_image = cv2.resize(no_image, image_size, interpolation = cv2.INTER_AREA)

    if image_count == 2:
        w = 2
        h = 1
        # resize to 960
        image_size = (960, 720)
        no_image = cv2.resize(no_image, image_size, interpolation = cv2.INTER_AREA)


    if len(imgs) != w*h:        
        pad_images = abs(len(imgs) - w*h)        
        for blank in range(pad_images):
            imgs.append(no_image)


    # resize

    imgs_resized = []

    for image in imgs:
        image_resized = cv2.resize(image, image_size, interpolation = cv2.INTER_AREA)

        a = datetime.datetime.now()
        time_stamp="%s:%s.%s" % (a.minute, a.second, str(a.microsecond)[:2])

            
        font = cv2.FONT_HERSHEY_SIMPLEX
        org = (50, 50)
        fontScale = 0.5
        color = (255, 255, 255)
        thickness = 1
        image_text = 'Display Time:' + time_stamp
        image_annotated = cv2.putText(image_resized, image_text, org, font, 
                        fontScale, color, thickness, cv2.LINE_AA)


        imgs_resized.append(image_annotated)


    imgmatrix = build_grid(imgs_resized, w, h)

    cv2.imshow("Grid", imgmatrix)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        #if 'q' key-pressed break out
        break



cv2.destroyAllWindows()
# close output window

# safely close video streams
for stream in streams:
    stream.stop()
