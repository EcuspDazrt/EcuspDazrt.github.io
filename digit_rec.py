import numpy as np

import io
from PIL import Image
import base64

layer_sizes = [784, 16, 16, 10]
lr = 0.01 # learning rate
epochs = 50

# filepaths for the images and labels
TRAIN_IMAGES = "train_images/train-images.idx3-ubyte"
TRAIN_LABELS = "train_labels/train-labels.idx1-ubyte"
TEST_IMAGES = "test_images/t10k-images.idx3-ubyte"
TEST_LABELS = "test_labels/t10k-labels.idx1-ubyte"

# w0 is weights between layers 0 and 1 (shape is (16, 784), since it the weights that transform a 784d vector (one for every activation in input layer) into a 16d vector (one dimension for every activation in the first hidden layer))
# w1 is weights between layers 1 and 2 (shape is (16, 16))
# w2 is weights between layers 2 and 3 (shape is (10, 16))

# b1 is biases for layer 1
# b2 is biases for layer 2
# b3 is biases for layer 3

def initialize_parameters():
    w0 = np.random.randn(16, 784) * 0.01
    w1 = np.random.randn(16, 16) * 0.01
    w2 = np.random.randn(10, 16) * 0.01
    b1 = np.random.randn(16, 1) * 0.01
    b2 = np.random.randn(16, 1) * 0.01
    b3 = np.random.randn(10, 1) * 0.01

    np.savez("/network.npz", w0=w0, w1=w1, w2=w2, b1=b1, b2=b2, b3=b3)

def load_parameters():
    data = np.load("/network.npz")
    w0 = data["w0"]
    w1 = data["w1"]
    w2 = data["w2"]
    b1 = data["b1"]
    b2 = data["b2"]
    b3 = data["b3"]

    return w0, w1, w2, b1, b2, b3

def relu(x):
    return np.maximum(0, x)

def softmax(x):
    e = np.exp(x - np.max(x))
    return e / np.sum(e, axis=0, keepdims=True)

def feed_forward(input, weights, biases):
    z1 = np.dot(weights[0], input) + biases[0]
    a1 = relu(z1)

    z2 = np.dot(weights[1], a1) + biases[1]
    a2 = relu(z2)

    z3 = np.dot(weights[2], a2) + biases[2]
    a3 = softmax(z3)

    return z1, a1, z2, a2, z3, a3

def feed_backward(x, y, z1, z2, A1, A2, A3, w1, w2):
    # error of the output layer (third layer)
    dz3 = A3 - y
    # backprop into the second hidden layer
    dA2 = np.dot(np.transpose(w2), dz3)
    dz2 = dA2 * (z2 > 0)
    # backprop into the third hidden layer
    dA1 = np.dot(np.transpose(w1), dz2)
    dz1 = dA1 * (z1 > 0)
    # calculate the gradients for the weights (first gradient for weights connecting layer 2 and 3, and biases for layer 3)
    dw2 = np.dot(dz3, np.transpose(A2))
    db3 = dz3
    # gradient for weights connecting layer 1 and 2, and biases for layer 2
    dw1 = np.dot(dz2, np.transpose(A1))
    db2 = dz2
    # gradient for weights connecting layer 0 and 1, and biases for layer 1
    dw0 = np.dot(dz1, np.transpose(x))
    db1 = dz1

    return dw0, db1, dw1, db2, dw2, db3

def find_output(x):
    max = 0
    index = 0
    for i in range(len(x)):
        if x[i] > max:
            max = x[i]
            index = i
    return index, x[index]

def read_images(path):
    with open(path, "rb") as file:
        data = file.read()

        magic = int.from_bytes(data[0:4], byteorder="big")
        num_images = int.from_bytes(data[4:8], byteorder="big")
        rows = int.from_bytes(data[8:12], byteorder="big")
        cols = int.from_bytes(data[12:16], byteorder="big")

        if magic != 2051:
            print("Invalid magic number; this is not a idx3 image file.")

        pixels = np.frombuffer(data, dtype=np.uint8, offset=16)
        pixels = pixels.reshape(num_images, rows, cols)

        pixels = pixels.astype(np.float32) / 255.0

        return pixels

def read_labels(path):
    with open(path, "rb") as file:
        data = file.read()

        magic = int.from_bytes(data[0:4], byteorder="big")
        num_labels = int.from_bytes(data[4:8], byteorder="big")

        if magic != 2049:
            print("Invalid magic number; this is not a idx1 label file.")

        labels = np.frombuffer(data, dtype=np.uint8, offset=8)

        return labels

def to_onehot(labels):
    output = []
    for label in labels:
        output.append(ideal_output(label))
    return output

def train(epochs, pixels, labels):
    w0, w1, w2, b1, b2, b3 = load_parameters()
    for epoch in range(epochs):
        print(f"epochs: {epoch} / {epochs}")
        for i in range(len(pixels)):
            x = pixels[i].reshape(-1, 1)
            y = np.array(labels[i]).reshape(-1, 1)
            z1, a1, z2, a2, z3, a3 = feed_forward(x, [w0, w1, w2], [b1, b2, b3])
            dw0, db1, dw1, db2, dw2, db3 = feed_backward(x, y, z1, z2, a1, a2, a3, w1, w2)

            w0 -= lr * dw0
            w1 -= lr * dw1
            w2 -= lr * dw2
            b1 -= lr * db1
            b2 -= lr * db2
            b3 -= lr * db3

    np.savez("/network.npz", w0=w0, w1=w1, w2=w2, b1=b1, b2=b2, b3=b3)

def get_accuracy(guesses):
    correct = 0
    count = 0
    for guess, label in guesses:
        if guess == label:
            correct += 1
        count += 1
    return f"{correct / count * 100}%"

def ideal_output(num):
    output = [0 for i in range(10)]
    output[num] = 1
    return output

def test_rand(image):
    _, _, _, _, _, output = feed_forward(image, weights, biases)
    return find_output(output)


# initialize weights and biases
w0, w1, w2, b1, b2, b3 = load_parameters()
weights = [w0, w1, w2]
biases = [b1, b2, b3]

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