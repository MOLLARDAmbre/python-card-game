from PIL import Image
import numpy as np
from tqdm import tqdm

im = Image.open("assets/4.png").convert('HSV')

def shift_pixel(hsv, shift):
    h, s, v = hsv
    h += shift
    if h >= 360:
        h -= 360
    return np.array([h, s, v])

def get_overall_hue(image):
    hue = 0
    nb_colors = 0
    im = np.array(image, dtype=np.uint8)
    for i in range(len(im)):
        for j in range(len(im[0])):
            if im[i][j][1] > 10:
                hue += im[i][j][0]
                nb_colors += 1
    return hue / nb_colors

def apply(image, shift):
    im = np.array(image, dtype=np.uint8)
    overall_hue = get_overall_hue(image)
    #shift = shift - overall_hue
    for i in tqdm(range(len(im))):
        for j in range(len(im[0])):
            try:
                im[i][j] = shift_pixel(im[i][j], shift)
            except:
                import pdb; pdb.set_trace()
    Image.fromarray(im, 'HSV').convert('RGB').save("assets/4_shift"+str(shift)+".png")
