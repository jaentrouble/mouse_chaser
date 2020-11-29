import pygame
import numpy as np
from multiprocessing import Queue, Process
from .common.constants import *
import os
import cv2
from pathlib import Path

class Viewer(Process):
    """
    This module shows a numpy array(3D) on a display
    """
    def __init__(self, width:int, height:int, event_queue:Queue,
                 image_queue:Queue, etc_queue:Queue, termQ:Queue,
                 fps=60):
        """
        Arguments
        ---------
        width : int
            Width of the screen (Default 720)
        height : int
            Height of the screen (Default 720)
        event_queue: Queue
            a Queue to put events that happended in Viewer
        image_queue: Queue
            a Queue to get image array
        etc_queue: Queue
            a Queue to get any meta info
        """
        super().__init__(daemon=True)
        self.size = (width, height)
        self._event_queue = event_queue
        self._image_queue = image_queue
        self._etc_queue = etc_queue
        self._fps = fps
        self._put_mouse_pos = False
        self._termQ = termQ
        self._icon_dir = Path('sources/icons')

    def run(self) :
        """
        Run viewer's mainloop
        """
        mainloop = True
        pygame.init()
        self._clock = pygame.time.Clock()
        self._screen = pygame.display.set_mode(self.size, pygame.RESIZABLE)
        self._background = pygame.Surface(self.size)
        self._allgroup = pygame.sprite.LayeredDirty()
        self._cursor = Cursor()
        self._cursor.add(self._allgroup)
        self._initiate_markers(self._allgroup)
        self._mouse_prev = pygame.mouse.get_pos()
        while mainloop :
            self._clock.tick(self._fps)
            if not self._image_queue.empty():
                datum = self._image_queue.get()
                image = datum.pop('image')
                if image.shape[0:2] != self.size:
                    self.size = image.shape[0:2]
                    self._screen = pygame.display.set_mode(self.size)
                    self._background = pygame.Surface(self.size)
                pygame.surfarray.blit_array(self._background, image)
                self._screen.blit(self._background, (0,0))

                # update markers
                for m_name, pos in datum.items():
                    self.update_marker_pos(m_name, pos)
            if not self._etc_queue.empty():
                q = self._etc_queue.get()
                for k, v in q.items():
                    if k == TERMINATE:
                        mainloop=False
            # close
            for event in pygame.event.get() :
                if event.type == pygame.QUIT :
                    mainloop = False
            ######################################
            # Keyboard events
                elif event.type == pygame.KEYDOWN :
                    if event.key == pygame.K_z:
                        self._event_queue.put({K_Z:None})
                    elif event.key == pygame.K_RETURN:
                        self._event_queue.put({K_ENTER:None})

                    # Prev / Next frame
                    elif event.key == pygame.K_1:
                        self._event_queue.put({K_1:None})
                    elif event.key == pygame.K_2:
                        self._event_queue.put({K_2:None})

                    # Markers
                    elif event.key == pygame.K_e:
                        self._event_queue.put({K_E:pygame.mouse.get_pos()})
                    elif event.key == pygame.K_r:
                        self._event_queue.put({K_R:pygame.mouse.get_pos()})
                    elif event.key == pygame.K_d:
                        self._event_queue.put({K_D:pygame.mouse.get_pos()})
                    elif event.key == pygame.K_f:
                        self._event_queue.put({K_F:pygame.mouse.get_pos()})
                    elif event.key == pygame.K_w:
                        self._event_queue.put({K_W:pygame.mouse.get_pos()})
                    elif event.key == pygame.K_q:
                        self._event_queue.put({K_Q:pygame.mouse.get_pos()})

                    elif event.key == pygame.K_i:
                        self._event_queue.put({K_I:pygame.mouse.get_pos()})
                    elif event.key == pygame.K_l:
                        self._event_queue.put({K_L:pygame.mouse.get_pos()})

            # Mouse events
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if pygame.mouse.get_pressed()[0]:
                        self._event_queue.put({MOUSEDOWN:pygame.mouse.get_pos()})
                    elif pygame.mouse.get_pressed()[2]:
                        self._event_queue.put({MOUSEDOWN_RIGHT:pygame.mouse.get_pos()})
                elif event.type == pygame.MOUSEBUTTONUP:
                    self._event_queue.put({MOUSEUP:None})

            self._allgroup.update()
            self._allgroup.clear(self._screen, self._background)
            self._allgroup.draw(self._screen)
            pygame.display.flip()
        self._termQ.put(TERMINATE)

    @property
    def size(self):
        """
        size : (width, height)
        """
        return (self._width, self._height)

    @size.setter
    def size(self, size:tuple):
        """
        size : (width, height)
        """
        self._width, self._height = size

    def _add_food_marker(self, group, pos=(0,0)):
        """Add one food marker
        Argument
        --------
        group : pygame group
            Group to add the marker
        pos : tuple
            Position of the marker. Default is (0,0)
        """
        new_marker = Marker(self._icon_dir/'food.png',pos)
        new_marker.add(group)
        self._marker_foods.append(new_marker)

    def _initiate_markers(self, group):
        """Initiate all markers

        Markers initiating here : 
            1 Nose marker
            # 2 Ear markers - deleted
            1 Head marker
            1 Tail marker
            1 Block marker
            2 Food markers
                - Note: Food markers will be saved in a list, so that it can
                        handle dynamic numbers of food
        Argument
        --------
        group : pygame group
            group that all markers should add into.
        """
        pos = (0,0)
        self._marker_nose = Marker(self._icon_dir/'nose.png',pos)
        group.add(self._marker_nose)

        # self._marker_ears = [
        #     Marker(self._icon_dir/'ear.png',pos),
        #     Marker(self._icon_dir/'ear.png',pos),
        # ]
        # for m in self._marker_ears:
        #     group.add(m)

        self._marker_head = Marker(self._icon_dir/'head.png',pos)
        group.add(self._marker_head)

        self._marker_tail = Marker(self._icon_dir/'tail.png',pos)
        group.add(self._marker_tail)

        self._marker_block = Marker(self._icon_dir/'block.png',pos)
        group.add(self._marker_block)

        self._marker_foods = [
            Marker(self._icon_dir/'food.png', pos),
            Marker(self._icon_dir/'food.png', pos),
        ]
        for m in self._marker_foods:
            group.add(m)

        self._marker_water = Marker(self._icon_dir/'water.png',pos)
        group.add(self._marker_water)

    def update_marker_pos(self, marker_type, pos):
        """Update marker's position.

        Parameters
        ----------
        marker_type : str
            Type of the marker. Available options are:
                'nose'
                # 'ear' - deleted
                'head'
                'food'
                'tail'
                'water'
                'block'
        pos : tuple or list of tuples
            - Tuple for single position
                'nose'
                'tail'
                'head'
                'water'
                'block'
            - List of tuples for multiple positions
                # 'ear' - deleted
                'food'
        """
        if 'nose' in marker_type:
            self._marker_nose.change_pos(pos)

        elif 'tail' in marker_type:
            self._marker_tail.change_pos(pos)

        elif 'water' in marker_type:
            self._marker_water.change_pos(pos)
        
        # elif 'ear' in marker_type:
        #     assert (len(pos) == 2) and isinstance(pos[0],(tuple,list))
        #     for m,p in zip(self._marker_ears, pos):
        #         m.change_pos(p)

        elif 'head' in marker_type:
            self._marker_head.change_pos(pos)
        
        elif 'block' in marker_type:
            self._marker_block.change_pos(pos)

        elif 'food' in marker_type:
            if len(pos)>0:
                assert isinstance(pos[0],(tuple,list))
            num_diff = len(self._marker_foods) - len(pos)
            if num_diff == 0:
                for m,p in zip(self._marker_foods, pos):
                    m.change_pos(p)
            elif num_diff > 0:
                for _ in range(num_diff):
                    m = self._marker_foods.pop()
                    m.kill()
                    del m
                for m,p in zip(self._marker_foods, pos):
                    m.change_pos(p)
            elif num_diff < 0:
                for m, p in zip(self._marker_foods, pos[:num_diff]):
                    m.change_pos(p)
                for p in pos[num_diff:]:
                    self._add_food_marker(self._allgroup,p)
    def close(self):
        pygame.quit()


class Cursor(pygame.sprite.DirtySprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((5,5))
        self.image.fill(CURSOR)
        self.rect = self.image.get_rect()
        self.visible = True
    
    def update(self):
        self.rect.center = pygame.mouse.get_pos()
        self.dirty = 1

    def change_color(self, color):
        self.image.fill(color)
        self.dirty = 1

class Marker(pygame.sprite.DirtySprite):
    """A marker showing each target's position
    
    A Marker image should be in size of 40 * 10 pixels
    """
    def __init__(self, img_path, pos):
        """
        Arguments
        ---------
        img_path : str or pathlib.Path
            image path for this marker
        """
        super().__init__()
        if isinstance(img_path, Path):
            img_path = str(img_path)
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).swapaxes(0,1)
        self.image = pygame.Surface(img.shape[:2])
        pygame.surfarray.blit_array(self.image, img)
        self.image.set_colorkey((0,0,0))
        self.rect = self.image.get_rect()
        self.rect.center = (pos[0]+15, pos[1])
        self.visible = True
    
    def change_pos(self, pos):
        self.rect.center = (pos[0]+15, pos[1])
        self.dirty = True