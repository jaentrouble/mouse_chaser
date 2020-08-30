import pygame
import numpy as np
from multiprocessing import Queue, Process
from .common.constants import *

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
        self._mouse_prev = pygame.mouse.get_pos()
        while mainloop :
            self._clock.tick(self._fps)
            if not self._image_queue.empty():
                image = self._image_queue.get()
                if image.shape[0:2] != self.size:
                    self.size = image.shape[0:2]
                    self._screen = pygame.display.set_mode(self.size)
                    self._background = pygame.Surface(self.size)
                pygame.surfarray.blit_array(self._background, image)
                self._screen.blit(self._background, (0,0))
            if not self._etc_queue.empty():
                q = self._etc_queue.get()
                for k, v in q.items():
                    if k == TERMINATE:
                        mainloop=False
            ###escape
            for event in pygame.event.get() :
                if event.type == pygame.QUIT :
                    mainloop = False
                elif event.type == pygame.KEYDOWN :
                    # if event.key == pygame.K_ESCAPE :
                    #     mainloop = False 
            ######################################
            # Keyboard events
                    if event.key == pygame.K_z:
                        self._event_queue.put({K_Z:None})
                    elif event.key == pygame.K_RETURN:
                        self._event_queue.put({K_ENTER:None})
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
