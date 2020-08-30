from sources.console import Console
from sources.viewer import Viewer
from sources.engine import Engine
from multiprocessing import Queue, set_start_method, freeze_support
from sources.common.constants import *

if __name__ == '__main__':
    set_start_method('spawn')
    freeze_support()
    imgQ = Queue()
    evntQ = Queue()
    etcQ = Queue()
    termQ =Queue()
    to_ConsoleQ = Queue()
    to_EngineQ = Queue()
    console_test = Console(to_ConsoleQ, to_EngineQ, termQ)
    viewer_test = Viewer(720, 300, evntQ, imgQ, etcQ, termQ)
    engine_test = Engine(to_EngineQ, to_ConsoleQ, imgQ, evntQ, etcQ)
    viewer_test.start()
    console_test.start()
    engine_test.start()
    termQ.get()