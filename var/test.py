import cv2
from numpy import where, array
import pyautogui
import pyaudio
import audioop
import os
import time
import psutil
import random
import configparser
import win32gui
import win32process
from PIL import ImageGrab



template = cv2.imread('.\\bobbery' + '.png', -1)
cv2.imshow("template", template)
time.sleep(100)
