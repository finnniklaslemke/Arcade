import pygame


darkmode = True
screen = None

WIDTH, HEIGHT = (0, 0)

def get_height():
    return pygame.display.get_surface().get_height()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_BLUE = (137, 207, 240)
PURPLE = (128, 0, 128)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREY = (50, 50, 50)
LIGHT_GREEN = (127, 255, 0)
GREEN = (0, 128, 0)
LIGHT_GREY = (127, 127, 127)

def get_border():
    return pygame.Rect(0, 0, WIDTH, HEIGHT)

border_width = 5

def get_rect_below_border(height=50):
    border = get_border()
    return pygame.Rect(
        border.left,
        border.bottom,
        border.width,
        height
    )

def get_rect_below_border_color():
    return BLACK if darkmode else WHITE

indicator_width = 10
indicator_height = 50

fonts = {}

buttons = {
    'standard_size': (300, 100),
    'height': 0,
    'width': 0
}
buttons['height'] = buttons['standard_size'][1]
buttons['width'] = buttons['standard_size'][0]

