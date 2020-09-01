import numpy as np
from multiprocessing import Process, Queue
from .common.constants import *
import os
from pathlib import Path
import cv2
import copy
import pickle

# To limit loop rate
from pygame.time import Clock

class Engine(Process):
    """Main process that calculates all the necessary computations

    Data structure
    [
        {
            'image' : np.array of the frame
            'marker name' : pos,
        },
    ]
    Data will be in order of the actual frame order
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

        self._data = []
        self._dummy_datum = {
            'image' : np.zeros((300,300,3),dtype=np.uint8),
            'nose' : (0,0),
            'ear' : [(0,0),(0,0)],
            'tail' : (0,0),
            'food' : [(0,0),(0,0)],
        }
        self._multiple_marker_idx = {
            'ear' : 0,
            'food' : 0,
        }

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
        self.reset_multi_marker_idx()

    def next_frame(self):
        last_idx = self.frame_idx
        self.frame_idx = min(self.frame_idx+1,self.frame_num)
        if self.frame_idx+1 > len(self._data):
            new_datum = copy.deepcopy(self._data[last_idx])
            new_datum['image'] = self.image
            self._data.append(new_datum)

    def prev_frame(self):
        self.frame_idx = max(self.frame_idx-1,0)

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
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self._frames.append(frame.swapaxes(0,1))
                if n % 500 == 0:
                    self._to_ConsoleQ.put(
                        {FRAMEIDX:f'loading : {n}frames loaded'}
                    )
                n += 1
            else :
                break
        cap.release()

        # Reset data
        self.frame_idx = 0
        self._data = []
        new_data = copy.deepcopy(self._dummy_datum)
        new_data['image'] = self.image
        self._data.append(new_data)

        print(f'{self.frame_num}frames loaded')
        print(f'shape : {self.shape}')
        return self.frame_num

    def reset_multi_marker_idx(self):
        """Resets all multiple_markers' indices to 0"""
        for k in self._multiple_marker_idx.keys():
            self._multiple_marker_idx[k] = 0

    def update_marker_pos(self, marker_type, pos):
        """Update marker's position
        If the marker type has multiple markers, it iterates
        
        Parameters
        ----------
        marker_type : str
            Type of the marker. Available options are:
                'nose'
                'ear'
                'food'
                'tail'
        pos : tuple
            Position of the marker
        """
        datum = self._data[self.frame_idx]
        single_markers = [
            'nose',
            'tail',
        ]
        multiple_markers = [
            'ear',
            'food',
        ]
        if marker_type in single_markers:
            datum[marker_type] = pos
        elif marker_type in multiple_markers:
            idx = self._multiple_marker_idx[marker_type] % len(datum[marker_type])
            self._multiple_marker_idx[marker_type] = idx
            datum[marker_type][idx] = pos
            self._multiple_marker_idx[marker_type] += 1

        self._updated = True

    def add_food_marker(self, pos):
        self._data[self.frame_idx]['food'].append(pos)
        self._updated = True

    def pop_food_marker(self):
        if len(self._data[self.frame_idx]['food']) >0:
            self._data[self.frame_idx]['food'].pop()
            self._updated = True

    def put_datum(self):
        self._imageQ.put(self._data[self.frame_idx])

    def save_data(self, vid_folder):
        """Saves to <vid_folder> / save / <n>.pck
        As every data has its image, there is no need to specify video name.
        """
        vid_folder = Path(vid_folder)
        save_folder = vid_folder / 'save'
        if not save_folder.exists():
            save_folder.mkdir()
        
        start_num = len(os.listdir(str(save_folder)))
        data_name = str(start_num) + '.pck'

        filename_data = save_folder/data_name
        
        with open(str(filename_data), 'wb') as f:
            pickle.dump(self._data, f)
        
        self._to_ConsoleQ.put({MESSAGE_BOX:'saved'})

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

                    elif k == SAVE:
                        self.save_data(v)

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

                    # Markers
                    elif k == K_F:
                        self.update_marker_pos('food',v)
                    elif k == K_E:
                        self.update_marker_pos('ear',v)
                    elif k == K_R:
                        self.update_marker_pos('nose',v)
                    elif k == K_D:
                        self.update_marker_pos('tail',v)
                    elif k == K_I:
                        self.add_food_marker(v)
                    elif k == K_L:
                        self.pop_food_marker()

                    # Prev / Next frame
                    elif k == K_1:
                        self.prev_frame()
                    elif k == K_2:
                        self.next_frame()


            if self._updated:
                self.put_datum()
                self._to_ConsoleQ.put(
                    {MARKERIDX:f'Marked until {len(self._data)-1} (idx)'}
                )
                self._updated = False