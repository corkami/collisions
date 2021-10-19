#!/usr/bin/env python3

# a JPG image collider

# Ange albertini 2018-2021

import sys
import struct

def comment_start(size):
  return b"\xff\xfe" + struct.pack(">H", size)

def comment(size, s=""):
  return comment_start(size) + s + b"\0" * (size - 2 - len(s))

def comments(s, delta=0):
  return comment(len(s) + delta, s)

fn1, fn2 = sys.argv[1:3]
with open(fn1, "rb") as f:
  d1 = f.read()
with open(fn2, "rb") as f:
  d2 = f.read()

with open("jpg1.bin", "rb") as f:
  block1 = f.read()
with open("jpg2.bin", "rb") as f:
  block2 = f.read()

# skip the signature, split by scans (usually the biggest segments)
c1 = d1[2:].split(b"\xff\xda")

if max(len(i) for i in c1) >= 65536 - 8:
  print("ERROR: The first image file has a segment that is too big!" +
    "Maybe save it as progressive or reduce its size/scans.")
  sys.exit()

ascii_art = b"".join(b"""
^^^^^^^^^^^^
/==============\\
|* JPG image  *|
|     with     |
|  identical   |
|   -prefix    |
| MD5 collision|
|              |
|  by          |
| Marc Stevens |
|  and         |
|Ange Albertini|
|  in 2018     |
|*            *|
\\==============/
vvvvvvvvvvvvvvvv""".splitlines())

suffix = b"".join([
  # fake comment to jump over the first image chunk (typically small)
  b"\xff\xfe",
    struct.pack(">H", 0x100 + len(c1[0]) - 2 + 4),
    ascii_art, # made to fit 

  # the first image chunk
  c1[0],

  # creating a tiny intra-block comment to host a trampoline comment segment
  b"".join([
      b"".join([
        # a comment over another comment declaration
        comments(
          b"\xff\xfe" +
          # +4 to reach the next intra-block
          struct.pack(">H", len(c) + 4 + 4),
          delta=2),
        b"\xff\xda",
        c
      ]) for c in c1[1:]
    ]),

    b"ANGE", # because we land 4 bytes too far

  d2[2:]
])

with open("collision1.jpg", "wb") as f:
  f.write(b"".join([
    block1,
    suffix
  ]))

with open("collision2.jpg", "wb") as f:
  f.write(b"".join([
    block2,
    suffix
  ]))
