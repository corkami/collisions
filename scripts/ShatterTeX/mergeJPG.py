#!/usr/bin/env python3

# apply sha1 mask

MASK = [
  0x0c, 0x00, 0x00, 0x02, 0xc0, 0x00, 0x00, 0x10, 0xb4, 0x00, 0x00, 0x1c, 0x3c, 0x00, 0x00, 0x04,
  0xbc, 0x00, 0x00, 0x1a, 0x20, 0x00, 0x00, 0x10, 0x24, 0x00, 0x00, 0x1c, 0xec, 0x00, 0x00, 0x14,
  0x0c, 0x00, 0x00, 0x02, 0xc0, 0x00, 0x00, 0x10, 0xb4, 0x00, 0x00, 0x1c, 0x2c, 0x00, 0x00, 0x04,
  0xbc, 0x00, 0x00, 0x18, 0xb0, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x0c, 0xb8, 0x00, 0x00, 0x10]


def apply_mask(d1):
  d = list(d1)
  for i,j in enumerate(MASK):
    d[64 * 2 + i - DELTA] = chr( ord(d[64 * 2 + i - DELTA]) ^ j)
    d[64 * 3 + i - DELTA] = chr( ord(d[64 * 3 + i - DELTA]) ^ j)
  return b"".join(d)

# PDF exact template
template = b"""%%PDF-1.3
%%\xe2\xe3\xcf\xd3


1 0 obj
<</Width 2 0 R/Height 3 0 R/Type 4 0 R/Subtype 5 0 R/Filter 6 0 R/ColorSpace 7 0 R/Length 8 0 R/BitsPerComponent 8>>
stream
%(hex)s
endstream
endobj

2 0 obj
%(width)i
endobj

3 0 obj
%(height)i
endobj

4 0 obj
/XObject
endobj

5 0 obj
/Image
endobj

6 0 obj
/DCTDecode
endobj

7 0 obj
/DeviceRGB
endobj

8 0 obj
%(imglen)i
endobj

9 0 obj
"""


DELTA = 0x55  # where the JPG starts relative to its block

import sys
import struct
import os

################################################################################
# various forms of 'random'

import random

################################################################################

def comment_segment(size, s=""):
  return "\xff\xfe" + struct.pack(">H", size) + s + "\0" * (size - 2 - len(s))


#reading data from actual JPGs

image1, image2, width, height, nbcomments = sys.argv[1:6]

nbcomments = int(nbcomments)
prefix = open("../../workshop/prefixes/12-shattered1.bin", "rb")
computation = prefix.read(64*3)

width, height = (int(i) for i in [width, height])

with open(image1, "rb") as f:
    r0 = f.read()
with open(image2, "rb") as f:
    r1 = f.read()


# we assume strictly identical App0 headers

data1, data2 = (r[2:] for r in [r0, r1])

################################################################################
# build the common blocks


block0 = b"".join([
  # start of image
  "\xff\xd8",

  # initial SoF and App0 are after a comment for crypto computing space
  # a comment segment until 0x7E, but we're inside the PDF
  comment_segment(0x79 - DELTA, "SHA-1 is dead!!!!!"), # we leave extra space for unique process markers


  # declare a comment segment, with a random size
  "\xff\xfe\x01", # comment segment marker and highest byte of the comment
  prefix.read(0x80), # our 2 collision blocks
])

block1 = apply_mask(block0)

# read the encoded lengths in the collision blocks
lengths = [struct.unpack(">H", b[0x7f - DELTA:0x7f - DELTA + 2])[0] for b in [block0, block1]]
maxlen, minlen = (lengths[0], lengths[1]) if (lengths[0] > lengths[1]) else (lengths[1], lengths[0])


# split the first image over Start Of Scan intervals
# (typically the biggest 'segments')
chunks1 = (data1).split("\xff\xda")
print("Image 1: %i SOS segments found" % (len(chunks1)))
print("max", max(len(i) for i in chunks1))
print("all", " ".join("%i" % len(i) for i in chunks1))

# build the file suffix
suffix = b"".join([
  # finish the smaller comment segment
  b"\0" * (minlen - 0x7f - 2),

  # *declare* an intermediate comment, starting after the smallest
  # covering the end of the biggest, and the first image data
  "\xff\xfe", struct.pack(">H", maxlen - minlen + len(chunks1[0]) - 2 + 4),
  b"\0" * (maxlen - minlen - 4),

  #the first image header
  chunks1[0]
])


# creating a tiny intra-block comment to host a 'bouncing' comment segment
for c in chunks1[1:]:
  suffix = b"".join([
    suffix,
    # a 6 character comment
    b"\xff\xfe",
      b"\x00\x06",
        # an inner comment jumping over the next chunk
        b"\xff\xfe",
          struct.pack(">H", (len(c) if len(c) < 0xfff0 else 0xBADD) + 4 + 4),  # +4 to reach the next intra-block
    b"\xff\xda",
      c,
  ])

suffix = b"".join([
  suffix,
  b"ANGE",
  data2
])

# let's revert fake SoS to comments
suffix = suffix.replace(b"\xff\xda", b"\xff\xfe", nbcomments)

#now we have the length of the image
imglen = len(block0) + len(suffix)

# now we can generate our colliding files prefix (incomplete PDF)
with open("prefix.pd_", "wb") as f:
  hex = b"".join([block0, suffix])
  contents = template % globals()
  whole_file = contents[:0xAD] + computation[0xAD:0xBD] + contents[0xBD:]
  f.write(whole_file)


# crop out the actual JPG for inclusion in the .TeX
with open("merged.jpg", "wb") as f:
  jpg = whole_file[whole_file.find("\xff\xd8"):]
  jpg = jpg[:jpg.rfind("\xff\xd9") + 2]
  f.write(jpg)