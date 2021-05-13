import os
import requests
import urllib.request
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

loaded_images = 0
def image_parse(bmp):
    global loaded_images
    loaded_images += 1

    if bmp[:4] == "http":
        if not os.path.exists("cache"):
            os.mkdir("cache")

        ending = "." + bmp.split("/")[-1].split(".")[-1]

        if not os.path.exists("cache/" + str(loaded_images) + ending):
            print_warning("waiting for images to download from server")
            try:
                urllib.request.urlretrieve(bmp, "./cache/" + str(loaded_images) + ending)
            except:
                print_error("failed to download images from server")
        bmp = "./cache/" + str(loaded_images) + ending

    return bmp
