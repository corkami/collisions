#!/usr/bin/env python

# script to collide JPEG2000 files
# Ange Albertini, December 2018

# as JP2 seems to enforce some atoms, a generic "atom/box" prefix starting with a `free` atom can't work.
# it needs a specific prefix that starts like a jp2 file.
# besides, the logic is the same as MP4. just no need to relocate anything.

import struct
import sys
import hashlib

def isValid(d):
  return d.startswith("\0\0\0\x0CjP  ") and d[0x10:0x18] == "ftypjp2 "

fn1, fn2 = sys.argv[1:3]

with open(fn1, "rb") as f:
  d1 = f.read()

with open(fn2, "rb") as f:
  d2 = f.read()

assert isValid(d1)
assert isValid(d2)

d1 = d1[0x20:]
d2 = d2[0x20:]

l1 = len(d1)
l2 = len(d2)

suffix = "".join([
  struct.pack(">I", 0x100 + 8), "free",
  "\0" * (0x100 - 8),
  struct.pack(">I", 8 + l1), "free",
  d1,
  d2,
  ])

with open("jp2-1.bin", "rb") as f:
  prefix1 = f.read()
with open("jp2-2.bin", "rb") as f:
  prefix2 = f.read()

col1 = prefix1 + suffix
col2 = prefix2 + suffix

md5 = hashlib.md5(col1).hexdigest()

if md5 == hashlib.md5(col2).hexdigest():
  print "md5: %s" % md5

  with open("collision1.jp2", "wb") as f:
    f.write(col1)

  with open("collision2.jp2", "wb") as f:
    f.write(col2)
