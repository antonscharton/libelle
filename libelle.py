import pygame
from pygame.locals import *
import os
from pathlib import Path
import numpy as np
from tqdm import tqdm
import time

# TODO
# backspace bug
# recording color
# proper zoom mapping (exponential instead of linear)


# settings
window_size = (1100, 700)
image_height = 400
pixel_per_label = 25
pixel_per_timestep = 2
fps = 20
autosave_time = 5    #minutes


# project settings
path_imagefolder = Path(r'C:\Users\Artem\Desktop\cv\app') #     <- specify
path_prjfile = Path('')



# utilities
def ltwh_from_cwh(center_x, center_y, width, height):
    return center_x -width/2, center_y - height/2, width, height



def show_image(screen, image):
    rect = image.get_rect()
    rect.center = (window_size[0]/2, image_height/2 + 10)
    screen.blit(image, rect)

def get_loc_from_glob(rect, global_pos):
    return (global_pos[0] - rect[0], global_pos[1] - rect[1])

def get_frame_from_mouse(rect, global_pos, zoom, max_frame):
    x = get_loc_from_glob(rect, global_pos)[0]
    x = x // (pixel_per_timestep * zoom)
    if x < 0:
        x = 0
    if x > max_frame:
        x = max_frame
    return x

def get_label_from_mouse(rect, global_pos):
    y = get_loc_from_glob(rect, global_pos)[1]
    y = y // pixel_per_label
    return y

def get_amount_label_rects(label):
    intervals = []
    start = None
    active = False
    for i, l in enumerate(label):
        if l == 1 and not active:
            start = i
            active = True
        elif l == 0 and active:
            intervals.append([start, i-1])
            active = False
    if active:
        intervals.append([start, i])
    intervals = [[interval[0], interval[1] - interval[0] + 1] for interval in intervals]
    return intervals




class Storage:
    labels = []
    images = []
    image_names_and_paths = []
    n = 0
    n_labels = 0
    path_imagefolder = None

    def load_images(self, path):
        self.path_imagefolder = path
        image_data = [(f.name, f.path) for f in os.scandir(path) if f.is_file() and ('.jpg' in f.name or
                                                                                     '.JPG' in f.name or
                                                                                     '.png' in f.name or
                                                                                     '.PNG' in f.name)]
        images = []
        for _, path in tqdm(image_data, desc='loading images'):
        #for _, path in image_data:

            # get width of image
            image = pygame.image.load(path)
            rect = image.get_rect()
            image = pygame.transform.scale(image, (rect[2]/rect[3]*image_height, image_height)).convert()
            images.append(image)

        self.images = images
        self.image_names_and_paths = image_data
        self.n = len(images)

    def add_label(self, i):
        assert self.n > 0, "no images have been loaded"
        if i is None:
            self.labels.append(np.zeros(self.n))
        else:
            self.labels.insert(i, np.zeros(self.n))
        self.n_labels = len(self.labels)

    def save(self, path):
        if self.n_labels == 0:
            print('nothing to save!')
        else:
            array = np.vstack(self.labels).T
            np.savetxt(path, array.astype('int'), fmt='%s', delimiter=' ')   # X is an array
            print('saved to ', path)

    def load(self, path):

        new_filename = "%s_%d.txt" % (self.path_imagefolder.name, time.time())
        new_path = os.path.join(self.path_imagefolder, new_filename)

        # if path not exist, make new file and return path
        if not (os.path.exists(path) and path.is_file()):
            path = new_path
            print("no path specified or no matching file found. Creating new file for annotation!\nAnnotation will be saved to:\n\n{}".format(new_path))

        # load file
        else:
            array = np.loadtxt(path, delimiter=' ').T

            # check if image sequence and annotation length matches
            if len(array[0]) == self.n:
                for row in array:
                    self.labels.append(row)
                self.n_labels = len(array)
            else:
                path = new_path
                print("Length of Annotation does not match number of images. Creating new file for annotation!\nAnnotation will be saved to:\n\n{}".format(new_path))


        return path

    def check(self):
        if self.n == len(self.labels[0]):
            print('number of images and length of annotation file matches!')
        else:
            print('number of images and length of annotation file DO NOT MATCH!\nCreating empty annotation file!')
            labels = []
            for i in range(self.n_labels):
                labels.append(np.zeros(self.n))
            self.labels = labels




def main():

    # init variables
    playing = False
    play_timer = 0
    save_timer = 0
    i_frame = 0
    i_label = None
    hovered_label = None
    label_temp = None
    running = True
    pressed = False
    moving_slider = False
    text_on = True
    recording = np.zeros(10)
    recording_class = np.zeros(10)
    zoom = 1

    # init pygame
    pygame.init()
    clock = pygame.time.Clock()
    clock2 = pygame.time.Clock()
    font = pygame.font.Font(os.path.join(os.path.dirname(__file__), 'cour.ttf'), 20)

    # screen surface
    screen = pygame.display.set_mode(window_size)

    # create storage and load image files # TODO sort?
    data = Storage()
    data.load_images(path_imagefolder)



    # load prj data
    path_save = data.load(path_prjfile)
    data.save(path_save)


    # create rects
    background_labelnames = pygame.Rect(0, image_height + 50, 20, data.n_labels*pixel_per_label)
    foreground_labelnames = pygame.Rect(0, image_height + 50, 20, pixel_per_label)
    background_labels = pygame.Rect(background_labelnames.right, image_height + 50, pixel_per_timestep*zoom*data.n, data.n_labels*pixel_per_label)
    background_buttons = pygame.Rect(background_labelnames.right, background_labels.bottom + 2, pixel_per_timestep*zoom*data.n, 30)
    background_slider = pygame.Rect(background_labelnames.right, background_buttons.bottom + 2, window_size[0] - background_labelnames.width, 15)
    foreground_slider = pygame.Rect(background_labelnames.right,  background_buttons.bottom + 4, window_size[0]- background_labelnames.width, 11)
    line = pygame.Rect(background_labelnames.right, background_labels.bottom + 2, zoom*pixel_per_timestep, 30)

    # create text
    text_headline = font.render('LIBELLE', True, (100, 100, 100))
    text_howto    = [   '\n\ngeneral keys',
                        '  [CTRL] + [S]                         save annotation file to specified path',
                        '  [LEFT ARROW], [RIGHT ARROW]          go one frame further / back',
                        '  [L]                                  add class before hovered class',
                        '  [L] + [CTRL] + [SHIFT] + [ALT]       delete hovered class',
                        '  [+]                                  zoom in',
                        '  [-]                                  zoom out',
                        '  [T]                                  text tool tips on / off',
                        ' ',
                        'play mode',
                        '  [SPACE]                              play / pause',
                        '  [BACKSPACE]                          go to frame 0',
                        '  [1] - [9]                            record on / off for class 1,2,...,9',
                        ' ',
                        'edit mode (when not playing)',
                        '  [LEFT MOUSE]                         paint label',
                        '  [LEFT MOUSE] + [LEFT CTRL]           erase label']
    print('\n'.join(text_howto))

    # main loop
    while running:

        # autosave
        save_timer += clock2.tick()
        if save_timer > autosave_time*60000:
            data.save(path_save)
            save_timer -= autosave_time*60000

        # player logic
        play_timer += clock.tick()
        if playing and play_timer >= 1000/fps:
            play_timer -= 1000/fps
            i_frame += 1

        if i_frame > data.n - 1:
            i_frame = data.n - 1
            pygame.mouse.set_pos(background_labels.right - 1, background_labels.bottom + 8)
            playing = False

        # recorder
        if playing and np.any(recording):
            for r, rec in enumerate(recording):
                if r < data.n_labels and rec:
                    data.labels[r][int(rec):i_frame] = 1

        # get pressed keys
        keys  = pygame.key.get_pressed()

        # get mouse position on label rect
        if not playing and (background_labels.collidepoint(pygame.mouse.get_pos()) or background_buttons.collidepoint(pygame.mouse.get_pos())):
            i_frame = get_frame_from_mouse(background_labels, pygame.mouse.get_pos(), zoom, data.n-1)

        # get hovered label
        if background_labels.collidepoint(pygame.mouse.get_pos()):
            hovered_label = get_label_from_mouse(background_labels, pygame.mouse.get_pos())
        else:
            hovered_label = None
        if hovered_label is not None:
            text_hovered_label = font.render('hovered class: {}'.format(hovered_label + 1), True, (150, 150, 150))
        else:
            text_hovered_label = font.render('hovered class: {}'.format(hovered_label), True, (150, 150, 150))

        # events
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False
            if not playing:
                if event.type == MOUSEBUTTONDOWN and event.button == 1:

                    if background_labels.collidepoint(event.pos) and keys[pygame.K_LCTRL]:
                        pressed = i_frame
                        i_label = get_label_from_mouse(background_labels, event.pos)
                        data.labels[i_label][i_frame] = 0
                    elif background_labels.collidepoint(event.pos):
                        pressed = i_frame
                        i_label = get_label_from_mouse(background_labels, event.pos)
                        data.labels[i_label][i_frame] = 1
                    elif background_buttons.collidepoint(event.pos) and background_buttons.width > window_size[0]:
                        moving_slider = True

                elif event.type == MOUSEBUTTONUP:
                    pressed = False
                    moving_slider = False
                elif event.type == MOUSEMOTION:

                    if pressed and keys[pygame.K_LCTRL]:
                        data.labels[i_label][i_frame] = 0
                        interval_s = pressed
                        interval_e = i_frame
                        if interval_s > interval_e:
                            interval_e = pressed
                            interval_s = i_frame
                        data.labels[i_label][interval_s:interval_e] = 0
                    elif pressed:
                        data.labels[i_label][i_frame] = 1
                        interval_s = pressed
                        interval_e = i_frame
                        if interval_s > interval_e:
                            interval_e = pressed
                            interval_s = i_frame
                        data.labels[i_label][interval_s:interval_e] = 1
                    elif moving_slider:
                        background_labels.move_ip(event.rel[0], 0)

            if event.type == KEYDOWN:

                # save
                if event.key == pygame.K_s:
                    mods = pygame.key.get_mods()
                    if mods & pygame.KMOD_CTRL:
                        data.save(path_save)
                # tool tips
                elif event.unicode == 't':
                    text_on = not text_on
                # zoom
                elif event.unicode == "+" and zoom < 100:
                    zoom += 1
                elif event.unicode == "-" and zoom > 1:
                    zoom -= 1
                elif event.key == pygame.K_LEFT:
                    playing = False
                    pygame.mouse.set_pos(line.left - zoom*pixel_per_timestep + 1, background_labels.bottom + 8)
                elif event.key == pygame.K_RIGHT:
                    playing = False
                    pygame.mouse.set_pos(line.left + zoom*pixel_per_timestep + 1, background_labels.bottom + 8)

                # label
                elif event.key == pygame.K_l:

                    mods = pygame.key.get_mods()
                    # delete
                    if mods & pygame.KMOD_CTRL and mods & pygame.KMOD_SHIFT and mods & pygame.KMOD_ALT:
                        if hovered_label is not None:
                            data.labels.pop(hovered_label)
                            data.n_labels -= 1
                    # create
                    else:
                        data.add_label(hovered_label)


                # stop
                elif event.key == K_BACKSPACE:
                    i_frame = 0
                    pygame.mouse.set_pos(background_labels.left + 1, background_labels.bottom + 8)
                    playing = False

                # play pause
                elif event.key == K_SPACE:
                    playing = not playing
                    if playing:
                        play_timer = 0
                    if not playing:
                        pygame.mouse.set_pos(line.left + 1, background_labels.bottom + 8)

                # play mode recording keys
                if playing:
                    numbers = np.array([event.unicode == str(i) for i in range(1, 10)])
                    if np.any(numbers):
                        num = numbers.nonzero()[0][0]
                        if recording[num]:
                            recording[num] = False
                        else:
                            recording[num] = i_frame




        # clean screen
        screen.fill((0, 0, 0))

        # show image
        show_image(screen, data.images[i_frame])

        # update UI
        # update label background
        if line.left >= window_size[0]:
            background_labels.left = background_labels.left - window_size[0]
        background_labels.height = data.n_labels*pixel_per_label
        background_labels.width = pixel_per_timestep*zoom*data.n
        background_buttons.width = background_labels.width
        background_buttons.top = background_labels.bottom + 2
        if background_labels.right < window_size[0]:
            background_labels.right = window_size[0]
        if background_labels.left > background_labelnames.right:
            background_labels.left = background_labelnames.right
        background_buttons.left = background_labels.left
        background_slider.top = background_buttons.bottom + 2
        background_labelnames.height = background_slider.bottom - background_labels.top

        if hovered_label is not None:
            foreground_labelnames.top = background_labelnames.top + hovered_label*pixel_per_label

        # update slider
        foreground_slider.top = background_slider.top + 2
        foreground_slider.width = (window_size[0] - background_labelnames.width)**2/background_labels.width
        foreground_slider.left = background_labelnames.width + (background_labelnames.right-background_labels.left)/background_labels.width*(window_size[0] - background_labelnames.width)

        # update line
        line.top = background_buttons.top
        line.width = zoom*pixel_per_timestep
        line.left = background_buttons.left + i_frame*zoom*pixel_per_timestep

        # draw backgrounds
        pygame.draw.rect(screen, (50, 50, 50), background_labels)
        pygame.draw.rect(screen, (50, 50, 50), background_buttons)
        pygame.draw.rect(screen, (50, 50, 50), background_slider)
        pygame.draw.rect(screen, (100, 100, 100), foreground_slider)
        pygame.draw.rect(screen, (100, 100, 100), line)

        # create and draw label foregrounds
        rects_labels = []
        rects_label_pos = [get_amount_label_rects(label) for label in data.labels]
        for i, rects in enumerate(rects_label_pos):
            rects_label = []
            for rect_pos in rects:
                rect = pygame.Rect(background_labels[0] + pixel_per_timestep*zoom*rect_pos[0], background_labels[1] + i*pixel_per_label, pixel_per_timestep*zoom*rect_pos[1], pixel_per_label)
                pygame.draw.rect(screen, (150, 150, 150), rect)

        # drae name background
        pygame.draw.rect(screen, (20, 20, 20), background_labelnames)
        if hovered_label is not None and not playing:
            pygame.draw.rect(screen, (20, 20, 100), foreground_labelnames)

        # draw label id names
        for i in range(data.n_labels):
            text = font.render(str(i+1), True, (150, 150, 150))
            screen.blit(text, (3, background_labels.top + pixel_per_label//2 - 10 +i*pixel_per_label))

        # show text
        screen.blit(text_headline, (20, 20))
        if text_on:
            screen.blit(text_hovered_label, (20, image_height-10))
            text_imagename = font.render('image name: {}'.format(data.image_names_and_paths[i_frame][0]), True, (150, 150, 150))
            screen.blit(text_imagename, (20, image_height-30))
            text_imageid = font.render('frame number: {}'.format(i_frame), True, (150, 150, 150))
            screen.blit(text_imageid, (20, image_height-50))

            text_save0 = font.render(str(path_save), True, (150, 150, 150))
            text_save = font.render('annotation will be saved to:', True, (150, 150, 150))
            re0= text_save0.get_rect()
            re0.right = window_size[0] - 5
            re0.bottom = background_labels.top - 2
            re= text_save.get_rect()
            re.right = window_size[0] - 5
            re.bottom = re.top - 1
            screen.blit(text_save0, re0)
            screen.blit(text_save, re)


        # update screen
        pygame.display.update()

    pygame.quit()
    #data.save(path_save)


if __name__ == '__main__':

    main()
