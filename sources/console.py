import tkinter as tk
from tkinter import ttk
from functools import partial
from multiprocessing import Process, Queue
from .common.constants import *
import os
from tkinter import filedialog, messagebox
from pathlib import Path

class Console(Process):
    """
    Console
    All the commands called by buttons, etc. are in console_f.py
    """
    def __init__(self, to_ConsoleQ:Queue, to_EngineQ:Queue, termQ:Queue):
        """
        Tk objects are not pickleable
        Initiate all windows when start()
        """
        super().__init__(daemon=True)
        self._to_ConsoleQ = to_ConsoleQ
        self._to_EngineQ = to_EngineQ
        self._termQ = termQ
        self._vid_name_list=[]

        self._info_str = (
            '1 : prev frame\n'
            '2 : next frame'
        )

    def initiate(self):
        self.root = tk.Tk()
        self.root.title('Mouse Chaser')
        self.mainframe = ttk.Frame(self.root, padding='3 3 12 12')
        self.mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.resizable(False, False)
        self._vid_name_var = tk.StringVar(value='No video loaded')
        self._frame_idx_var = tk.StringVar(value='No video loaded')
        self._info_var = tk.StringVar(value=self._info_str)

        # # Configure Top-left threshold setting menu ###########################
        self.frame_frame = ttk.Frame(self.mainframe, padding='5 5 5 5')
        self.frame_frame.grid(column=0, row=0, sticky = (tk.W, tk.N))
        self.label_frame_idx = ttk.Label(self.frame_frame,
                                        textvariable=self._frame_idx_var)
        self.label_frame_idx.grid(column=0, row=0, sticky=(tk.W))

        # Configure Top-Right Prev/Next menu ##################################
        self.frame_prevnext = ttk.Frame(self.root, padding='5 5 5 5')
        self.frame_prevnext.grid(column=2, row=0, sticky = (tk.E, tk.N))
        self.button_prev = ttk.Button(self.frame_prevnext,
                                      text='Prev',
                                      command=self.button_prev_f)
        self.button_prev.grid(column=0, row=0)
        self.button_next = ttk.Button(self.frame_prevnext,
                                      text='Next',
                                      command=self.button_next_f)
        self.button_next.grid(column=0, row=1)
        self.button_open = ttk.Button(self.frame_prevnext,
                                      text='Open',
                                      command=self.button_open_f)
        self.button_open.grid(column=0, row=2)
        self.label_vid_name = ttk.Label(self.frame_prevnext,
                                        textvariable=self._vid_name_var)
        self.label_vid_name.grid(column=0, row=3)

        # Configure Bottom-Left Info menu #####################################
        self.frame_info = ttk.Frame(self.root, padding='5 5 5 5')
        self.frame_info.grid(column=0, row=1, sticky=(tk.W, tk.S))
        self.label_info = ttk.Label(self.frame_info,
                                    textvariable=self._info_var)
        self.label_info.grid(column=0, row=0)

        # Configure Bottom-Right Save menu ####################################
        self.frame_save = ttk.Frame(self.root, padding='5 5 5 5')
        self.frame_save.grid(column=2, row=1, sticky=(tk.E, tk.S))
        self.button_save = ttk.Button(self.frame_save, text='Save',
                                      command=self.button_save_f)
        self.button_save.grid(column=2, row=1, sticky=(tk.E, tk.S))

        # Set weights of frames ###############################################
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)


    def run(self):
        self.initiate()
        self.button_open_f(ask=False)
        self.root.after(16, self.update)
        self.root.mainloop()
        self._termQ.put(TERMINATE)



    def button_open_f(self, ask=True):
        if ask:
            answer = messagebox.askyesno(message='This will reset everything.'\
                                                '\n Continue?')
            if not answer: return
        dirname = filedialog.askdirectory()
        if dirname == '':
            pass
        else:
            self._vid_folder = dirname
            self._vid_name_list = []
            self._vid_idx = 0
            for f in os.listdir(self._vid_folder):
                if f.endswith(VIDEO_FORMATS):
                    self._vid_name_list.append(f)
            if len(self._vid_name_list) > 0 :
                self._to_EngineQ.put({
                    NEWVID:os.path.join(self._vid_folder,
                            self._vid_name_list[self._vid_idx])
                })
                self._vid_name_var.set(self._vid_name_list[self._vid_idx])

    def button_next_f(self):
        answer = messagebox.askyesno(message='All unsaved values will disappear.\
            \nContinue?')
        if answer:
            if len(self._vid_name_list) > 0 :
                self._vid_idx = (self._vid_idx+1)%len(self._vid_name_list)
                self._to_EngineQ.put({
                    NEWVID:os.path.join(self._vid_folder,
                            self._vid_name_list[self._vid_idx])
                })
                self._vid_name_var.set(self._vid_name_list[self._vid_idx])

    def button_prev_f(self):
        answer = messagebox.askyesno(message='All unsaved values will disappear.\
            \nContinue?')
        if answer:
            if len(self._vid_name_list) > 0 :
                self._vid_idx = (self._vid_idx-1)%len(self._vid_name_list)
                self._to_EngineQ.put({
                    NEWVID:os.path.join(self._vid_folder,
                            self._vid_name_list[self._vid_idx])
                })
                self._vid_name_var.set(self._vid_name_list[self._vid_idx])

    def button_save_f(self):
        self._to_EngineQ.put({SAVE:None})


    def message_box(self, string):
        messagebox.showinfo(message=string)

    def update(self):
        if not self._to_ConsoleQ.empty():
            q = self._to_ConsoleQ.get()
            for k,v in q.items():
                if k == FRAMEIDX:
                    self._frame_idx_var.set(v)
        self.root.after(16, self.update)