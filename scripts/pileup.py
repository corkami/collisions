#!/usr/bin/env python

# script to craft MD5 pileups (multi-collisions) of
# a PDF document, a PE executable, a PNG image and an MP4 video

# Ange Albertini 2019


import os
import sys
import struct
import hashlib
import zlib


def dprint(s):
  DEBUG = True
  DEBUG = False
  if DEBUG:
    print("D " + s)

def setDWORD(d, offset, s):
  assert len(s) == 4
  return "".join([
    d[:offset],
    s,
    d[offset+4:]
  ])

# MP4 functions ###############################################################


def relocateMP4(d, delta):
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



# PDF functions ###############################################################


def EnclosedString(d, starts, ends):
  off = d.find(starts) + len(starts)
  return d[off:d.find(ends, off)]

def getCount(d):
  s = EnclosedString(d, "/Count ", "/")
  count = int(s)
  return count

template = """%%PDF-1.3
%%\xC2\xB5\xC2\xB6

1 0 obj
<</Length 2 0 R>>
stream
%(buffer)s
endstream
endobj

2 0 obj
%(lenBuffer)i
endobj 

3 0 obj
<<
  /Type /Catalog
  /Pages 4 0 R
>>
endobj

4 0 obj  
<</Type/Pages/Count %(count)i/Kids[%(kids)s]>>
endobj
"""


# PE functions ################################################################


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
    d = setDWORD(d, offset, struct.pack("l", PhysOffset + delta) )
  return d


# Prefix constants ############################################################

# required offset of the PE header after the prefix
PEOFFSET = 0x560

# where section starts
ALIGN = 0x1000

SECTIONEXTRA = 0x00 # amount of stuff to copy before sections start in case (for UPX?)

# main ########################################################################


if len(sys.argv) == 1:
  print("PDF-PE MD5 collider")
  print("Usage: pdf-pe.py <file.pdf> <file.exe> <file.png> <file.mp4>")
  sys.exit()

with open(sys.argv[2], "rb") as f:
  pe = f.read()
with open(sys.argv[3], "rb") as f:
  png = f.read()[8:] # skip the magic
with open(sys.argv[4], "rb") as f:
  mp4 = f.read()

assert pe.startswith("MZ")

PEoff, HdrLen, NumSec, SecTblOff, SectsStart = getPEhdr(pe)
lenPE = len(pe[PEoff:])

os.system('mutool merge -o merged.pdf dummy.pdf %s' % (sys.argv[1]))

with open("merged.pdf", "rb") as f:
  dm = f.read()

count = getCount(dm) - 1

kids = EnclosedString(dm, "/Kids[", "]")

# we skip the first dummy that should be 4 0 R because of the `mutool merge`
assert kids.startswith("4 0 R ")
kids = kids[6:]

dm = dm[dm.find("5 0 obj"):]
dm = dm.replace("/Parent 2 0 R", "/Parent 4 0 R")
dm = dm.replace("/Root 1 0 R", "/Root 3 0 R")

pe = relocateSections(pe, SecTblOff, NumSec, ALIGN - SectsStart)
Sections = pe[SectsStart - SECTIONEXTRA:]

buffer = "".join([
  pe[PEoff:PEoff+HdrLen],
    (ALIGN - HdrLen - PEOFFSET - SECTIONEXTRA) * "\0",
  Sections,
  ])

lenPE = len(buffer) # for PNG file

buffer += "CRC3" + png
lenPEPNG = len(buffer) # for MP4 file

buffer += relocateMP4(mp4, lenPEPNG + 0x560) # hardcoded offset of the PE in our computed prefix

lenBuffer = len(buffer) # placeholder
# we need to align the PE header
stage1 = template % locals()
deltaPDF = stage1.find("stream\n") + len("stream\n")

buffer = "\0" * (PEOFFSET - deltaPDF + len("2 0 R") - len("%i" % lenBuffer)) + buffer
with open("hacked.pdf", "wb") as f:
  f.write(template % locals())
  f.write(dm)

# let's adjust offsets - don't use -g to keep the length object 2 temporarily unused by mutool transform
# the direct length reference added by mutool will be replaced by a reference to object 2 via the prefix

# (yes, errors will appear because we modified objects without adjusting XREF)
print
print "KEEP CALM and IGNORE THE NEXT ERRORS"
os.system('mutool clean hacked.pdf cleaned.pdf')

with open("cleaned.pdf", "rb") as f:
  cleaned = f.read()

with open("pileup-pdf.bin", "rb") as f:
  prefixPDF = f.read()
with open("pileup-pe.bin", "rb") as f:
  prefixPE = f.read()
with open("pileup-mp4.bin", "rb") as f:
  prefixMP4 = f.read()
with open("pileup-png.bin", "rb") as f:
  prefixPNG = f.read()


# MP4 free atom ###############################################################

cleaned = setDWORD(cleaned, 0x540,struct.pack(">L", lenPEPNG + 0x20))
cleaned = setDWORD(cleaned, 0x544, "free")


# PNG fixes 

cleaned = prefixPNG + cleaned[0x540:]
# crc of collision chunk
cleaned = setDWORD(cleaned, 0x550, struct.pack(">L", zlib.crc32(cleaned[0x70:0x550]) & 0xffffffff))

# aNGE chunk
cleaned = setDWORD(cleaned, 0x554, struct.pack(">L", lenPE + 4))
cleaned = setDWORD(cleaned, 0x558, "aNGE")
cleaned = setDWORD(
  cleaned,
  0x560 + lenPE,
  struct.pack(">L", zlib.crc32(cleaned[0x558:0x560 + lenPE]) & 0xffffffff))


with open("collision.pdf", "wb") as f:
  f.write(prefixPDF + cleaned[0x540:])
with open("collision.mp4", "wb") as f:
  f.write(prefixMP4 + cleaned[0x540:])
with open("collision.exe", "wb") as f:
  f.write(prefixPE  + cleaned[0x540:])
with open("collision.png", "wb") as f:
  f.write(cleaned)

os.remove('merged.pdf')
os.remove('hacked.pdf')
os.remove('cleaned.pdf')
