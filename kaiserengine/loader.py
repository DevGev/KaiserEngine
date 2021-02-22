import os
from kaiserengine.debug import *

def load_ivan(ivan_file):
    force_path(ivan_file)
    real_path = os.path.realpath(ivan_file)
    dir_path = os.path.dirname(real_path)
    img_load = []

    try:
        with open(ivan_file) as F:
            ivan_file = eval(F.read())
    except:
        print_error("Failed to load ivan file: " + ivan_file)

    for img in ivan_file:
        path = dir_path + "/" + img
        force_path(path)
        img_load.append(path) 

    if len(img_load) == 0:
        print_error("Failed to load ivan file: " + ivan_file)

    return img_load
