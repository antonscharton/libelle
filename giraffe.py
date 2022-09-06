import pygame
from pygame.locals import *
import os
import threading
from pathlib import Path
import numpy as np
from tqdm import tqdm
import time

# project settings
##############################################################################
path_imagefolder = r'C:\Users\scharton\Documents\aufnahmen\2022_08_03-09_39_10' # <- specify
path_prjfile = r'' # <- specify optionally
##############################################################################

# settings
window_size = (1100, 700)
image_height = 1000
autosave_time = 5           # in minutes
