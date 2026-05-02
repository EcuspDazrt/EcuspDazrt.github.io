import numpy as np

import io
from PIL import Image
import base64

# <---------- Initialize model params ---------->
weights = []
biases = []
def load_parameters():
    data = np.load("/network.npz")
    weights.append(data["w0"])
    weights.append(data["w1"])
    weights.append(data["w2"])
    biases.append(data["b1"])
    biases.append(data["b2"])
    biases.append(data["b3"])

load_parameters()



# <---------- Model structure ---------->
def relu(x):
    return np.maximum(0, x)

def softmax(x):
    e = np.exp(x - np.max(x))
    return e / np.sum(e, axis=0, keepdims=True)

def feed_forward(input_layer):
    z1 = np.dot(weights[0], input_layer) + biases[0]
    a1 = relu(z1)

    z2 = np.dot(weights[1], a1) + biases[1]
    a2 = relu(z2)

    z3 = np.dot(weights[2], a2) + biases[2]
    a3 = softmax(z3)

    return z1, a1, z2, a2, z3, a3



# <---------- Utility funcs ---------->
def get_guess_and_confidence(x):
    maximum = 0
    index = 0
    for i in range(len(x)):
        if x[i] > maximum:
            maximum = x[i]
            index = i
    return index, x[index]

def test_rand(image):
    _, _, _, _, _, output = feed_forward(image)
    return get_guess_and_confidence(output)



# <---------- Func called by web ---------->
def predict(payload: dict):
    data = payload['image']
    data = data.split(',')[1]
    image_bytes = base64.b64decode(data)

    img = Image.open(io.BytesIO(image_bytes))

    img_gray = img.convert('L')
    img_arr = np.array(img_gray)
    img_arr = img_arr / 255.0

    digit, confidence = test_rand(img_arr.reshape(-1, 1))
    return {'digit': digit, 'confidence': confidence}