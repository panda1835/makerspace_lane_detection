import cv2 as cv
import yaml

# Import custom modules
import image_processing

# Read config
with open('./config.yaml', 'r') as f:
    data = yaml.load(f, Loader=yaml.loader.SafeLoader)

# Define constant
FRAME_WIDTH = data['frame_width'][0]
FRAME_HEIGHT = data['frame_height'][0]

import matplotlib.pyplot as plt

if __name__ == "__main__":
    camera = cv.VideoCapture(0)
    camera.set(cv.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    camera.set(cv.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    camera.set(cv.CAP_PROP_FPS, 30)
    
    while True:
        _, img = camera.read()
        try:
            img = image_processing.process_image(img, fill_region=True)
            cv.imshow('lane detection',img)
        except Exception as e:
            print(str(e))
        key = cv.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    camera.release()
    cv.destroyAllWindows()