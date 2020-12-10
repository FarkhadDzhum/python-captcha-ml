import os
import cv2
import numpy as np
from keras.models import load_model

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
MODEL_PATH = os.path.join(os.getcwd(), "model", "my_model.h5")
symbols = "0123456789"


def predict(filepath):
    model = load_model(MODEL_PATH)
    img = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
    img = img / 255.0
    res = np.array(model.predict(img[np.newaxis, :, :, np.newaxis]))
    ans = np.reshape(res, (4, 10))
    l_ind = []
    for a in ans:
        l_ind.append(np.argmax(a))
    capt = ""
    for l in l_ind:
        capt += symbols[l]
    return capt


if __name__ == "__main__":
    predict("./captchas/captcha.jpg")
