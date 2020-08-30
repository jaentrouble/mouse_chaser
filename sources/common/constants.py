# Engine Constants ############################################################
CURSOR = (0,0,0)
EAR = (0,255,0)
NOSE = (0,255,255)
FOOD = (255,0,0)

DEFAULT_MP_RATIO = 0.30
DEFAULT_MP_PIXEL = 91
DEFAULT_MP_MICRO = 50

NEWIMAGE = 0
NEWMASK = 1

MODE_MASK = 10
MODE_IMAGE = 11
MODE_NONE = 12
MODE_SET_MEM = 13
MODE_SET_CELL = 14
MODE_DRAW_MEM = 15
MODE_DRAW_CELL = 16
MODE_FILL_CELL = 17
MODE_FILL_MP_RATIO = 18
MODE_DRAW_BOX = 19
MODE_SHOW_BOX = 20
MODE_HIDE_BOX = 21
MODE_CANCEL_CLIP = 22
MODE_CLIP = 23
MODE_CONFIRM_CLIP = 24

SET_MEM = 100
SET_CELL = 101
SET_RATIO = 102

DRAW_OFF = 201
DRAW_MEM = 202
DRAW_CELL = 203
DRAW_CANCEL = 204
DRAW_BOX = 205

FILL_CELL = 301
FILL_MP_RATIO = 302
FILL_LIST = 303
FILL_DELETE = 304
FILL_SAVE = 305
FILL_MICRO = 306

TERMINATE = -1





# Viewer Constants ############################################################
MOUSEDOWN = 401
MOUSEUP = 402
MOUSEPOS = 403
MOUSEDOWN_RIGHT = 404

MESSAGE_BOX = 601

# Use same numbers as pygame.K_* + 1000
K_Z = 1122
K_ENTER = 1013

# Console Constants ###########################################################
IMAGE_FORMATS = ('.jpg', '.png', '.jpeg', '.tif', '.tiff')