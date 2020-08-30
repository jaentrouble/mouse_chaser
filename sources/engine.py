import numpy as np
from multiprocessing import Process, Queue
from .common.constants import *
import os
import json
from pathlib import Path
import cv2

# To limit loop rate
from pygame.time import Clock

class Engine(Process):
    """
    Main process that calculates all the necessary computations
    """
    # If the image is not updated, check if self._updated is switched to True
    def __init__(self, to_EngineQ:Queue, to_ConsoleQ:Queue,
                 imageQ:Queue, eventQ:Queue, etcQ:Queue):
        super().__init__(daemon=True)
        # Initial dummy frame
        self._frames = [np.zeros((300,300,3),dtype=np.uint8)]
        self.frame_idx = 0
        # Queues
        self._to_EngineQ = to_EngineQ
        self._to_ConsoleQ = to_ConsoleQ
        self._imageQ = imageQ
        self._eventQ = eventQ
        self._etcQ = etcQ

    @property
    def image(self):
        """
        This is a base image. Do not directly modify self._image
        """
        return self._image.copy()

    @image.setter
    def image(self, image:np.array):
        """
        Must be a shape of (width, height, 3)
        """
        if len(image.shape) != 3 and image.shape[2] != 3:
            raise TypeError('Inappropriate shape of image')
        self._image = image.astype(np.uint8)
        self._shape = self._image.shape
        self.set_empty_mask()
        self._updated = True

    @property
    def shape(self):
        """
        Do not implement shape.setter
        Shape is dependent to image and should only be setted with image
        """
        return self._shape

    @property
    def frame_idx(self):
        """Index of current frame"""
        return self._frame_idx

    @property
    def frame_idx(self, idx:int):
        """Sets current image to the idx"""
        self._frame_idx = idx
        self.image=self._frames[idx]

    def load_vid(self, vid_name):
        """Load a video and returns total frame number
        Parameter
        ---------
        vid_name : str
            String of the video's path

        Return
        ------
        num_frames : int
            Total number of frames
        """
        cap = cv2.VideoCapture(vid_name)
        self._frames = []
        while(cap.isOpened):
            ret, frame = cap.read()
            self._frames.append(frame)
        cap.release()
        return len(self._frames)


    def run(self):
        mainloop = True
        self._clock = Clock()
        while mainloop:
            self._clock.tick(60)
            if not self._to_EngineQ.empty():
                q = self._to_EngineQ.get()
                for k, v in q.items():
                    if k == TERMINATE:
                        mainloop = False

            if not self._eventQ.empty():
                q = self._eventQ.get()
                for k,v in q.items():
                    if k == MOUSEDOWN:
                        pass
                    elif k == MOUSEDOWN_RIGHT:
                        pass
                    elif k == MOUSEUP:
                        pass
                    elif k == MOUSEPOS:
                        pass
                    # Keyboard events
                    elif k == K_Z:
                        pass
                    elif k == K_B:
                        pass
                    elif k == K_ENTER:
                        pass
                    elif k == K_ESCAPE:
                        pass


            if self._updated:
                self.put_image()
                self._updated = False