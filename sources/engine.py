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
        # Queues
        self._to_EngineQ = to_EngineQ
        self._to_ConsoleQ = to_ConsoleQ
        self._imageQ = imageQ
        self._eventQ = eventQ
        self._etcQ = etcQ

        self._updated = False

    @property
    def frame_num(self):
        return len(self._frames)

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

    @frame_idx.setter
    def frame_idx(self, idx:int):
        """Sets current image to the idx"""
        self._frame_idx = idx
        self.image=self._frames[idx]
        self._to_ConsoleQ.put(
            {FRAMEIDX:f'{self._frame_idx}/{self.frame_num-1}'}
        )

    def next_frame(self):
        self.frame_idx = (self.frame_idx+1) % self.frame_num

    def prev_frame(self):
        self.frame_idx = (self.frame_idx-1) % self.frame_num

    def load_vid(self, vid_name):
        """Load a video and returns total frame number
        Parameter
        ---------
        vid_name : str
            String of the video's path

        Return
        ------
        frame_num : int
            Total number of frames
        """
        print('loading...')
        self._vid_name = vid_name
        cap = cv2.VideoCapture(vid_name)
        self._frames = []
        n = 0
        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret:
                self._frames.append(frame.swapaxes(0,1))
                if n % 500 == 0:
                    self._to_ConsoleQ.put(
                        {FRAMEIDX:f'loading : {n}frames loaded'}
                    )
                n += 1
            else :
                break
        cap.release()
        self.frame_idx = 0
        print(f'{self.frame_num}frames loaded')
        print(f'shape : {self.shape}')
        return self.frame_num


    def put_image(self):
        self._imageQ.put(self.image)

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

                    elif k == NEWVID:
                        self.load_vid(v)

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
                    elif k == K_ENTER:
                        pass

                    # Prev / Next frame
                    elif k == K_1:
                        self.prev_frame()
                    elif k == K_2:
                        self.next_frame()


            if self._updated:
                self.put_image()
                self._updated = False