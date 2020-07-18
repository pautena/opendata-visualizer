#!/usr/local/bin/python3

import cv2
import argparse
import os



FPS=24


def main():
    # Construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-ext", "--extension", required=False, default='png', help="extension name. default is 'png'.")
    ap.add_argument("-o", "--output", required=False, default='tmp/output.mp4', help="output video file")
    args = vars(ap.parse_args())

    # Arguments
    dir_path = './tmp/frames'
    ext = args['extension']
    output = args['output']

    images = []
    for f in os.listdir(dir_path):
        if f.endswith(ext):
            images.append(f)
    images.sort()

    # Determine the width and height from the first image
    image_path = os.path.join(dir_path, images[0])
    frame = cv2.imread(image_path)
    cv2.imshow('video',frame)
    height, width, channels = frame.shape

    print(f'frame: width: {width}, height: {height}')

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Be sure to use lower case
    out = cv2.VideoWriter(output, fourcc, FPS, (width, height))

    for image in images:
        for _ in range(0,FPS):
            image_path = os.path.join(dir_path, image)
            frame = cv2.imread(image_path)

            out.write(frame) # Write out frame to video

            cv2.imshow('video',frame)
            if (cv2.waitKey(1) & 0xFF) == ord('q'): # Hit `q` to exit
                break

    # Release everything if job is finished
    out.release()
    cv2.destroyAllWindows()

    print("The output video is {}".format(output))



if __name__ == "__main__":
    main()