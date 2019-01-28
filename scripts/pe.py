#!/usr/bin/env python

# a script to collide arbitrary Windows Executables with MD5

# Ange Albertini 2018

# takes 2 PE,
# gets both PE headers+DD+sections
# moves them next to each other,
# adjust offsets of section tables
# copy sections next to each other
# update SizeOfHeaders of file 2

import sys, struct, hashlib, os

def getPEhdr(d):
  PEoffset = d.find("PE\0\0")
  peHDR = d[PEoffset:]

  Machine = struct.unpack("H", peHDR[4:4+2])[0]

  SecCount = struct.unpack("h", peHDR[0x6:0x6+2])[0]
  bits = None
  if Machine == 0x014C:
    bits = 32
  elif Machine == 0x8664:
    bits = 64
  if bits is None:
    print "ERROR: unknown arch"
    sys.exit()

  NumDiffOff = 0x74 if bits == 32 else 0x84
  NumDD = struct.unpack("l", peHDR[NumDiffOff:NumDiffOff+4])[0]

  SecTblOff = NumDiffOff + 4 + NumDD * 2 * 4

  # get the offset of the first section
  SectsStart = struct.unpack("l", peHDR[SecTblOff+0x14:SecTblOff+0x14+4])[0]

  PElen = SecTblOff + SecCount * 0x28

  return PEoffset, PElen, SecCount, PEoffset + SecTblOff, SectsStart


def relocateSections(d, SecTblOff, SecCount, delta):
  for i in range(SecCount):
    offset = SecTblOff + i*0x28 + 0x14
    PhysOffset = struct.unpack("l", d[offset:offset+4])[0]
    d = "".join([
      d[:offset],
      struct.pack("l", PhysOffset + delta),
      d[offset+4:]
      ])
  return d


fn1, fn2 = sys.argv[1:3]

# the following 2 depends on computed collision blocks
# to leave room for 9 collision blocks after CPC
HEADER1OFF = 0x2C0
# arbitrary length to support most PE headers
HEADER2OFF = 0x480


# too lazy to get optimal file alignment :p
SECTIONSOFF = 0x1000

with open("pe1.bin", "rb") as f:
  prefix1 = f.read()
with open("pe2.bin", "rb") as f:
  prefix2 = f.read()

with open(fn1, "rb") as f:
  d1 = f.read()
with open(fn2, "rb") as f:
  d2 = f.read()


# best PE validation ever :p
assert d1.startswith("MZ")
assert d2.startswith("MZ")

PEoff1, HdrLen1, NumSec1, SecTblOff1, SectsStart1 = getPEhdr(d1)
PEoff2, HdrLen2, NumSec2, SecTblOff2, SectsStart2 = getPEhdr(d2)

if HdrLen1 > HEADER2OFF - HEADER1OFF:
  print "ERROR: PE header 1 is too big"
  sys.exit()

if HdrLen2 > SECTIONSOFF - HEADER2OFF:
  print "ERROR: PE header 2 is too big"
  sys.exit()

#SizeOfHeader increased
d2 = "".join([
  d2[:PEoff2 + 0x54],
  struct.pack("l", SECTIONSOFF),
  d2[PEoff2 + 0x54 + 4:]
  ])

d1 = relocateSections(d1, SecTblOff1, NumSec1, SECTIONSOFF - SectsStart1)
Sections1 = d1[SectsStart1:]
Sections2 = d2[SectsStart2:]

# let's hope the first batch of sections are aligned to file Alignments ;)
OffSec2 = len(Sections1) + SECTIONSOFF

d2 = relocateSections(d2, SecTblOff2, NumSec2, OffSec2 - SectsStart2)

suffix = "".join([
  d1[PEoff1:PEoff1+HdrLen1],
    (HEADER2OFF - (HEADER1OFF + HdrLen1)) * "\0",
  d2[PEoff2:PEoff2+HdrLen2],
    (SECTIONSOFF - (HEADER2OFF + HdrLen2)) * "\0",
  Sections1,
  Sections2
  ])

with open("collision1.exe", "wb") as f:
  f.write(prefix1 + suffix)
with open("collision2.exe", "wb") as f:
  f.write(prefix2 + suffix)

md5 = hashlib.md5(prefix1 + suffix).hexdigest()

assert md5 == hashlib.md5(prefix2 + suffix).hexdigest()

print "Success!"
print "Common MD5: %s" % md5
