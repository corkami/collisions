#!/usr/bin/env python

# script to collide "MP4"-based files with specific `ftyp`
# Ange Albertini, December 2019

import struct
import sys
import hashlib


def dprint(s):
  DEBUG = True
  DEBUG = False
  if DEBUG:
    print("D " + s)


def relocate(d, delta):
  # finds and relocates all Sample Tables Chunk Offset tables
  # TODO: support 64 bits `co64` tables ()
  offset = 0
  tablecount = d.count("stco")
  dprint("stco found: %i" % tablecount)
  for i in range(tablecount):
    offset = d.find("stco", offset)
    dprint("current offset: %0X" % offset)

    length   = struct.unpack(">I", d[offset-4:offset])[0]
    verflag  = struct.unpack(">I", d[offset+4:offset+8])[0]
    offcount = struct.unpack(">I", d[offset+8:offset+12])[0]

    if verflag != 0:
      dprint(" version/flag not 0 (found %X) at offset: %0X" % (verflag, offset+4))
      continue

    # length, type, verflag, count - all 32b
    if (offcount + 4) * 4 != length:
      dprint(" Atom length (%X) and offset count (%X) don't match" % (length, offcount))
      continue

    dprint(" offset count: %i" % offcount)
    offset += 4 * 3
    offsets = struct.unpack(">%iI" % offcount, d[offset:offset + offcount * 4])
    dprint(" offsets (old): %s" % `list(offsets)`) 
    offsets = [i + delta for i in offsets]
    dprint(" (new) offsets: %s" % `offsets`)

    d = d[:offset] + struct.pack(">%iI" % offcount, *offsets) + d[offset+offcount*4:]

    offset += 4 * offcount

  dprint("")
  return d


def freeAtom(l):
  return struct.pack(">I", l) + "free" + "\0" * (l - 8)


def isValid(d):
  # fragile check of validity
  return d.startswith("\0\0\0") and d[:32].count("ftyp") > 0



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
  relocate(d1, 0x1C0 + 8 - 0x20),
  relocate(d2, 0x1C0 + 8 - 0x20 + l1),
  ])

# 32b length prefix

with open("mp4s1.bin", "rb") as f:
  prefix1 = f.read()
with open("mp4s2.bin", "rb") as f:
  prefix2 = f.read()

col1 = prefix1 + suffix
col2 = prefix2 + suffix

md5 = hashlib.md5(col1).hexdigest()

if md5 == hashlib.md5(col2).hexdigest():
  print "common md5: %s" % md5

  with open("collisions1.mp4", "wb") as f:
    f.write(col1)

  with open("collisions2.mp4", "wb") as f:
    f.write(col2)
