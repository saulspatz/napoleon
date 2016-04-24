# newColor.py
# Change color in SVG file
import argparse
import re

parser = argparse.ArgumentParser(description='Change colors in SVG file')
parser.add_argument('oldFile', help='source file path')
parser.add_argument('newFile', help='target file path')
parser.add_argument('oldColor', help='RGB value in hex of color to replace')
parser.add_argument('newColor', help='RGB value in hex of replacement color')

args = parser.parse_args()

with open(args.oldFile) as fin, open(args.newFile,'w') as fout:
    text = fin.read()
    text = re.sub(args.oldColor, args.newColor, text)
    fout.write(text)
    