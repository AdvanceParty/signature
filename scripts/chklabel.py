import argparse
import numpy as np
import matplotlib.pyplot as plt
import random

parser = argparse.ArgumentParser()
parser.formatter_class = argparse.RawTextHelpFormatter
parser.description = "Make sure indexed labels in one npy array match the image data in another npy array."
parser.add_argument(
    "-g",
    "--glyphs",
    required=True,
    help="Numpy array of image"
)
parser.add_argument(
    "-l",
    "--labels",
    required=True,
    help="Numpy array of labes.")
args = parser.parse_args()



def main(fname_glyphs, fname_labels):
    glyphs = np.load(fname_glyphs)
    labels = np.load(fname_labels)
    results = []
    fig = plt.figure(figsize=(2,5))
    for x in range(10):
        rnd = random.randint(0,glyphs.shape[0])
        results.append((glyphs[rnd], labels[rnd]))
        sp = plt.subplot(2, 5, x+1)
        sp.title.set_text(chr(labels[rnd]))
        plt.imshow(glyphs[rnd].reshape(20,20))
        plt.axis('off')
    
    #plt.subplots_adjust(hspace=.25)
    plt.show()

if __name__ == "__main__":
    main(args.glyphs, args.labels)

