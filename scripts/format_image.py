import sys
from pathlib import Path
import os
import argparse
from PIL import Image, ImageOps, ImageEnhance
from tqdm import tqdm

COLORMODE = {
    "g": "L",
    "m": "L",
    "r": "RGB"
}


def rgb(value):
    try:
        result = tuple(map(int, str.split(value, ",")))
        if (len(result) != 3):
            raise Exception()
    except Exception as e:
        return False

    return result


description = '''Prepare an image for ML processing'''

parser = argparse.ArgumentParser()
parser.formatter_class = argparse.RawTextHelpFormatter
parser.description = description
parser.add_argument(
    "-i",
    "--input",
    required=True,
    help="File to be converted"
)
parser.add_argument(
    "-o",
    "--output",
    required=True,
    help="Name and path to save converted file.")

parser.add_argument(
    "-c",
    "--colormode",
    default="g",
    choices=["g", "r", "m"],
    help="g [greyscale], r [rgb], or m [monochrome b+w]")
parser.add_argument(
    "-p",
    "--prefix",
    default="",
    help="Prefix string for exported filenames. Optional."
)
parser.add_argument(
    "-t",
    "--threshold",
    default=40,
    type=int,
    help="Threshold for conversion to monochrome. Pixels with a value > threshold will be white, the rest black. low numbers are best. Default is 40.")

parser.add_argument(
    "-W",
    "--width",
    type=int,
    help="Optionally specify a target width for the formatted image. See also --aspect and --height."
)

parser.add_argument(
    "-H",
    "--height",
    type=int,
    help="Optionally specify a target height for the formatted image. See also --aspect and --width."
)

parser.add_argument(
    "-r",
    "--resample",
    default=Image.LANCZOS,
    type=int,
    help="Set the reampling filter for resizing images. Accepts all the methods available to PIL.Image (https://pillow.readthedocs.io/en/stable/reference/Image.html). Image.BICUBIC is default, for best balance between speed and quality."
)

parser.add_argument(
    "-n",
    "--number",
    type=int,
    default=0,
    help="Set a maximum number of files to be converted. Useful for testing conversion settings before converting a large set of images. If 0, then all available images will be converted."
)

parser.add_argument(
    "-I",
    "--invert",
    action="store_true",
    default=False,
    help="Invert colors in image."
)

parser.add_argument(
    "-a",
    "--aspect",
    type=str,
    default='fill',
    choices=['preserve', 'ignore', 'fill'],
    help="preserve (deault option): keep aspect ratio of original image when resizing. Resized image will not exceed either of the supplied --width or --height arguments.\nignore: Aspect ratio of original image will be discarded. Resized image will exactly match supplied --width and --height values.\nfill: aspect ration will be preserved, but a background color will be added to fill up any space required to for new image to be exact match of supplied --width and --height arguments."
)

parser.add_argument(
    "-f",
    "--fillcolor",
    type=rgb,
    default='0,0,0',
    help="Background color to fill empty space when resampling image to a fixed w,h while preserving aspect ratio. Supply as RGB values from 0->255 (eg: 200,200,100 )."
)


args = parser.parse_args()


def read(fpath):
    try:
        return Image.open(fpath)
    except:
        raise Exception(f"Error reading file: {fpath}")


def convert_mode(img):
    if args.colormode:
        try:
            colormode = COLORMODE[args.colormode]
            if (img.mode != colormode):
                img = img.convert(colormode)
            if args.colormode in ["m","g"]:
                img = ImageOps.grayscale(img)
            if args.colormode == "m":
                img = ImageOps.posterize(img, 2)
                img = ImageOps.equalize(img)
                img = img.point(lambda x: 255 if x > args.threshold else 0, mode="L")

        except Exception as e:
            raise Exception(e)

    return img


def resize(img):
    if args.width or args.height:

        imgW, imgH = img.size
        dim = [args.width or imgW, args.height or imgH]
        bg_size = list(dim)

        if (args.aspect != 'ignore'):

            if args.width and args.height:
                measure = 0 if args.width < args.height else 1
            else:
                measure = 0 if args.width is not None else 1

            preserve = 1 if measure == 0 else 0
            ratio = dim[measure]/img.size[measure]
            dim[preserve] = round(img.size[preserve] * ratio)

        img = img.resize(dim, args.resample)

        if args.aspect == 'fill':
            bg = Image.new("RGB", bg_size, args.fillcolor)
            bg.convert(img.mode)
            bg.paste(img)
            img = bg

        return img


def save_image(img, fpath):
    try:
        img.save(fpath)
    except ValueError:
        raise Exception(f"Could not determine filetype of {img}")
    except IOError as e:
        raise Exception(f"IO Error: Unable to write to {fpath}.{e}")


def invert(img):
    if (args.invert):
        try:
            iMode = img.mode
            
            if iMode != "RGB":
                img =  img.convert("RGB")
            
            img = ImageOps.invert(img)

            if iMode != "RGB":
                img = img.convert(iMode)
        except Exception as e:
           raise Exception (e) 
    return img


def process(img):
    try:

        # manipuilate image
        img = convert_mode(img)
        img = invert(img)
        img = resize(img)

        return img

    except Exception as e:
        raise Exception(e)


def get_error_summary(errors):
    bullet = ' • '
    summary = ''

    if len(errors) > 0:
        summary += f"\n{len(errors)} images could not be converted:"
        summary += f"\n{bullet}"
        summary += f"\n{bullet}".join(errors)
        summary += "\n"

    return summary


def dir_is_writable(dir):
    return os.path.isdir(dir) and os.access(dir, os.W_OK)


def main():
    errors = []
    converted_count = 0

    if not dir_is_writable(args.output):
        sys.exit(
            f"\n**Failed**\n • <{args.output}> does not exist or is not writable.")

    src_path = Path(args.input)
    file_count = args.number if args.number > 0 else len(os.listdir(args.input))
    pbar = tqdm(os.listdir(args.input), total=file_count)    
    for entry in pbar:

            f = src_path / entry

            if not entry.startswith('.') and f.is_file():
                converted_count += 1
                try:
                    img = read(f)
                    img = process(img)
                    save_image(img,  os.path.join(args.output, args.prefix+entry))
                except Exception as e:
                    # print("OOPS")
                    errors.append(f"{entry}: {e}")
                    pass

            if (args.number > 0) and (converted_count >= args.number):
                break
    # summarise results
    print(f"Converted {converted_count} images.")
    print(get_error_summary(errors))


if __name__ == "__main__":
    main()
