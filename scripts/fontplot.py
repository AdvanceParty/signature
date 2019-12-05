import sys
from pathlib import Path
import tqdm
import os
import argparse
import math
import pandas as pd
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


# 33  -> 47   [space] ! " # $ % + ' ( ) * + , - . /
# 48  -> 57   digits 0-9
# 58  -> 64   : ; < = > ? @
# 65  -> 90   A-Z
# 91  -> 96   [ \ ] ^ _ `
# 97  -> 122  a-z
# 123 -> 126  { | } ~

parser = argparse.ArgumentParser()
parser.formatter_class = argparse.RawTextHelpFormatter
parser.description = 'Convert csv data from font lib dataset ito numpy arrays for DCGAN'
parser.add_argument(
    "-i",
    "--input",
    required=True,
    help="Directory of font csv files"
)
parser.add_argument(
    "-o",
    "--output",
    required=True,
    help="Path to directory for saving the exported numpy data."
)
parser.add_argument(
    "-n",
    "--number",
    default=0,
    type=int,
    help="max number od files to process. 0 = all files in directory. Default: 0."
)

args=parser.parse_args()

min_char = 33
max_char = 126
#fname = "/Users/gilfewster/dev/ap/handwriting/writing_samples/fonts/AGENCY.csv"

def load_font_data(path):
    data = pd.read_csv(path)
    data = pd.concat([
        data.iloc[:, data.columns.get_loc('m_label')],
        data.iloc[:, data.columns.get_loc('r0c0'):data.columns.get_loc('r19c19')+1]], axis=1)

    char_filter = (data.m_label.between(min_char, max_char))
    chars = data[char_filter]
    char_count = len(chars.index)

    pixels = chars.iloc[:, chars.columns.get_loc('r0c0'):chars.columns.get_loc('r19c19')+1].to_numpy().reshape(char_count, 20, 20)   
    char_codes = chars.iloc[:, chars.columns.get_loc('m_label')].to_numpy()

    return (pixels, char_codes) 

def dir_is_writable(dir):
    return os.access(dir, os.W_OK)

def main():
    errors = []
    summary= []
    glyphs=None
    labels=None
    src_path = Path(args.input)

    file_count = args.number if args.number > 0 else len(os.listdir(args.input))
    print(f"Converting {args.number} files. Let's rock this.")

    for entry in os.listdir(args.input):

        f = src_path / entry
        fname = entry.strip('.csv')

        if not entry.startswith(".") and f.is_file():
            try:
                (new_glyphs, new_labels) = load_font_data(f)
                glyphs = new_glyphs if (glyphs is None) else np.concatenate((glyphs, new_glyphs), axis=0)
                labels = new_labels if (labels is None) else np.concatenate((labels, new_labels), axis=0)
                summary.append(f"font: {fname}| glyph count: {new_glyphs.shape[0]} | label count: {new_labels.shape[0]}")
                print(f" > Converted [{new_glyphs.shape[0]}|{new_labels.shape[0]}] [glyphs|labels] from {fname}.")
            except Exception as e:
                errors.append(f"{entry}: {e}")

        if (args.number > 0 ) and (len(summary) >= args.number):
            break;

    try:
        fname_labels = f"{args.output}_labels"
        fname_glyphs = f"{args.output}_glyphs"
        fname_summary = f"{args.output}_summary.txt"
        np.save(fname_glyphs, glyphs)
        np.save(fname_labels, labels)
        summary_fo = open(fname_summary,"w")
        summary_fo.write('\n'.join(summary).replace('|',','))
        summary_fo.close()
    except Exception as e:
        print(e)

    print()
    print(f"Saved:\n {fname_labels}.npy\n {fname_glyphs}.npy\n {fname_summary}\n")
    print(f"Converted {len(summary)} files.")
    print(f"Converted data has shape {glyphs.shape}")

    if (len(errors)):
        print("\n--- Errors ---")
        print("\n".join(errors))

if __name__ == "__main__":
    main()
