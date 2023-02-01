import argparse
from multiprocessing import cpu_count
import cv2
import os
import numpy as np
from PIL import Image
from pathlib import Path

CWD = os.getcwd()
TARGET_FOLDER_PATH = os.path.join(CWD, "cropped_images")
CASCADE_CLASSIFIER_PATH = "./face_classifier/facedetector.xml"


def face_detector(image_path: str) -> None:
    if os.path.isfile(image_path):
        # configure target output dir
        image_name = image_path.replace('\\', '/').replace(".", "_").split("/")[-1]
        target_folder_path = os.path.join(TARGET_FOLDER_PATH,image_name)
        Path(target_folder_path).mkdir(parents=True, exist_ok=True)
        # initialize image variables
        image = None
        gray_image = None
        try:
            image = cv2.imread(image_path)
            # convert image to grayscale
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        except Exception as e:
            print(e)
        
        face_classifier = cv2.CascadeClassifier(CASCADE_CLASSIFIER_PATH)
        detection_result = face_classifier.detectMultiScale(gray_image)
        # save detected faces
        count = 0
        for index, (x, y, w, h) in enumerate(detection_result):
            count += 1
            detected_image = np.array(image[y:y + h, x:x + w])
            detected_image_name = os.path.join(target_folder_path, f"image_{count}.png")
            cv2.imwrite(detected_image_name, detected_image)
        # summary
        print(f"Detected {len(detection_result)} face(s)")
    else:
        print("Invalid image path!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Human face detector')
    parser.add_argument('--image', required=True, help='Input image path')
    args = parser.parse_args()

    if args.image:
        face_detector(args.image)
    else:
        print("Something went wrong...")
