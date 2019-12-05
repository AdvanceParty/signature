import os
import argparse
import cv2
from PIL import Image
import numpy as np

description = '''Convert a directory of images into a numpy array and save data to disk.
Exported array will have shape [image_count, image_width, image_height].

NOTE: All images in directory must be the same width and height.'''

parser = argparse.ArgumentParser()
parser.formatter_class = argparse.RawTextHelpFormatter
parser.description = description
parser.add_argument(
    '--grey',
    action='store_true',
    default=True,
    help="Boolean flag. If included, the umages will be exported as single-channel greyscale data. If excluded, images data will be exported as three channel rgb."
)
parser.add_argument(
    "--src",
    required=True,
    help="Directory of images for conversion"
)
parser.add_argument(
    "--outfile",
    required=True,
    help="name and path to save the converted data")

parser.add_argument(
    "--max",
    type=int,
    default=0,
    help="Specifiy a maximum number of images to include in the exported .npy array"
)

args = parser.parse_args()


def pretty_print_failed_conversions(fnames):
    if (len(fnames) > 0):
        print(f"\nCould not convert {len(fnames)} file(s):")
        print(*[' • {}'.format(i) for i in fnames], sep="\n")
        print()


def convert_files():
    failed = []
    converted = []

    for filename in os.listdir(args.src):

        fpath = os.path.join(args.src, filename)

        mode = cv2.IMREAD_GRAYSCALE if args.grey else cv2.IMREAD_COLOR
        img = cv2.imread(f"{fpath}", mode)

        if (img is not None):

            converted.append(img)
            print(f"converted: {len(converted)}")
        else:
            failed.append(filename)
        
        if (args.max > 0 ) and len(converted) >= args.max:
            break;

    return (np.array(converted), failed)


def save_data(data):
    try:
        np.save(args.outfile, data)
        return True
    except:
        return False


def main():
    (data, failed) = convert_files()
    print()
    print(f"Converted {data.shape[0]} images to array with shape {data.shape}")
    pretty_print_failed_conversions(failed)

    try:
        success = save_data(data)
        print(f"Saved numpy array to\n{args.outfile}.npy")
    except:
        print(f" *** Error saving data to disk ***")


if __name__ == "__main__":
    main()
