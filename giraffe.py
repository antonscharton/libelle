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
path_imagefolder = r'C:\Users\Artem\Desktop\in car test set\images_pose' # <- specify
path_annotationfolder = r'C:\Users\Artem\Desktop\in car test set\annotations_pose' # <- specify
##############################################################################

# settings
window_size = (1100, 700)
image_height = 600
autosave_time = 5           # in minutes


class Storage:
    labels = []
    images = []
    image_names_and_paths = []
    n = 0
    n_labels = 0
    path_imagefolder = None
    no_image = None
    running = True

    def __init__(self, path, data_sort_mode = 'num_'):
        self.path_imagefolder = path
        image_names = np.array([f.name for f in os.scandir(path) if f.is_file() and ('.jpg' in f.name or
                                                                                     '.JPG' in f.name or
                                                                                     '.png' in f.name or
                                                                                     '.PNG' in f.name)])

        self.image_names_and_paths = [(name, os.path.join(path, name)) for name in image_names]
        self.n = len(self.image_names_and_paths)

        # load first image and no image
        image = pygame.image.load(self.image_names_and_paths[0][1])
        rect = image.get_rect()
        image = pygame.transform.scale(image, (rect[2]/rect[3]*image_height, image_height)).convert()
        self.images.append(image)

        no_image = pygame.image.load(os.path.join(Path().resolve(), 'no_image.png'))
        rect = no_image.get_rect()
        self.no_image = pygame.transform.scale(no_image, (rect[2]/rect[3]*image_height, image_height)).convert()


    def load_images(self):
        images = []
        for _, path in tqdm(self.image_names_and_paths, desc='loading images'):
        #for _, path in self.image_names_and_paths:

            if self.running:

                # get width of image
                image = pygame.image.load(path)
                rect = image.get_rect()
                image = pygame.transform.scale(image, (rect[2]/rect[3]*image_height, image_height)).convert()
                images.append(image)

                # load into memory each 200 images
                if len(images) % 200 == 0:
                    self.images = images

        self.images = images
        self.n = len(images)


def show_image(screen, data, i):
    try:
        image = data.images[i]
    except:
        image = data.no_image

    rect = image.get_rect()
    rect.center = (window_size[0]/2, image_height/2 + 10)
    screen.blit(image, rect)
    return rect

def create_new_pose():
    points = {'nose': (0.50, 0.10),
              'left_eye': (0.60, 0.05),
              'right_eye': (0.40, 0.05),
              'left_ear': (0.65, 0.05),
              'right_ear': (0.35, 0.05),
              'left_shoulder': (0.80, 0.25),
              'right_shoulder': (0.20, 0.25),
              'left_elbow': (0.92, 0.50),
              'right_elbow': (0.08, 0.50),
              'left_wrist': (0.95, 0.70),
              'right_wrist': (0.05, 0.70),
              'left_hip': (0.70, 0.55),
              'right_hip': (0.30, 0.55),
              'left_knee': (0.70, 0.75),
              'right_knee': (0.30, 0.75),
              'left_ankle': (0.70, 0.95),
              'right_ankle': (0.30, 0.95)
              }
    return points

def coco_map_i_to_name(k):
    i = {0: 'nose',
              1: 'left_eye',
              2: 'right_eye',
              3: 'left_ear',
              4: 'right_ear',
              5: 'left_shoulder',
              6: 'right_shoulder',
              7: 'left_elbow',
              8: 'right_elbow',
              9: 'left_wrist',
              10: 'right_wrist',
              11: 'left_hip',
              12: 'right_hip',
              13: 'left_knee',
              14: 'right_knee',
              15: 'left_ankle',
              16: 'right_ankle'
              }
    return i[k]

def pose_from_list(points):
    d = {}
    for i, point in enumerate(points):
        d[coco_map_i_to_name(i)] = point
    return d


def visualize_sceleton(surface, rect, pose):
    coco_skeleton = np.array([[15,13],[13, 11],[16, 14],[14, 12],[11, 12],[5, 11],[6, 12],
                        [5, 6],[5, 7],[6, 8],[7, 9],[8,10],[1,2],[0,1],[0,2],[1,3],[2,4],[3,5],[4, 6]])
    for sk in coco_skeleton:
        p1_x, p1_y = pose[coco_map_i_to_name(sk[0])]
        p2_x, p2_y = pose[coco_map_i_to_name(sk[1])]
        p1_x = rect.left + rect.width*p1_x
        p1_y = rect.top + rect.height*p1_y
        p2_x = rect.left + rect.width*p2_x
        p2_y = rect.top + rect.height*p2_y
        pygame.draw.line(surface, (0, 0, 0), (p1_x, p1_y), (p2_x, p2_y), width=5)

    rects = []
    for key, point in pose.items():
        x = rect.left + point[0]*rect.width
        y = rect.top + point[1]*rect.height
        r = pygame.draw.circle(surface, (0, 0, 0), (x, y), 10, 0)
        rects.append(r)
    return rects

def rects_to_pose(image_rect, point_rects):
    points = []
    for rect in point_rects:
        points.append(((rect.center[0] - image_rect.left)/image_rect.width,
                       (rect.center[1] - image_rect.top)/image_rect.height))
    return pose_from_list(points)

def main():

    running = True
    i_frame = 0
    dragging = False


    # init pygame
    pygame.init()
    pygame.display.set_caption('CAMELOPARDALIS')

    # screen surface
    screen = pygame.display.set_mode(window_size)

    # create storage and load image files
    data = Storage(Path(path_imagefolder))
    thread = threading.Thread(target=data.load_images, name='load_images')
    thread.start()

    # prelimary
    pose_estimations = {}

    # main loop
    while running:

        # clean screen
        screen.fill((0, 0, 0))

        # show image
        rect = show_image(screen, data, i_frame)

        # create new pose if not done yet
        name = data.image_names_and_paths[i_frame][0]
        if name not in pose_estimations:
            pose_estimations[name] = create_new_pose()

        print(pose_estimations[name])
        # show pose
        point_rects = visualize_sceleton(screen, rect, pose_estimations[name])


        # events
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
            if event.type == KEYDOWN:
                if event.key == K_LEFT and i_frame > 0:
                    i_frame -= 1
                elif event.key == K_RIGHT and i_frame < len(data.images)-1:
                    i_frame += 1

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                for rect in point_rects:
                    if rect.collidepoint(event.pos):
                        print('dragging ', rect)
                        dragging = rect
                        break
            elif event.type == MOUSEBUTTONUP:
                print('dragging stopped ', dragging)
                dragging = False
            elif event.type == MOUSEMOTION and dragging:
                dragging.move_ip(event.rel)


        # save pose
        pose_estimations[name] = rects_to_pose(rect, point_rects)


        # update screen
        pygame.display.update()

    # quit
    pygame.quit()

main()
