#!/usr/bin/env python

# script to craft MD5 collisions of a PDF and a PE
# Ange Albertini 2019

import os
import sys
import struct
import hashlib


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
%(pe)s
endstream
endobj

2 0 obj
%(lenPE)i
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
    d = "".join([
      d[:offset],
      struct.pack("l", PhysOffset + delta),
      d[offset+4:]
      ])
  return d


# Prefix constants ############################################################


# required offset of the PE header after the prefix
PEOFFSET = 0x2C0

# where section starts
ALIGN = 0x1000

SECTIONEXTRA = 0x00 # amount of stuff to copy before sections start in case (for UPX)

# main ########################################################################


if len(sys.argv) == 1:
  print("PDF-PE MD5 collider")
  print("Usage: pdf-pe.py <file1.pdf> <file2.exe>")
  sys.exit()

with open(sys.argv[2], "rb") as f:
  pe = f.read()

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

pe = "".join([
  pe[PEoff:PEoff+HdrLen],
    (ALIGN - HdrLen - PEOFFSET - SECTIONEXTRA) * "\0",
  Sections,
  ])

# we need to align the PE header
stage1 = template % locals()
deltaPDF = stage1.find("stream\n") + len("stream\n")

pe = "\0" * (PEOFFSET - deltaPDF + len("2 0 R") - len("%i" % lenPE)) + pe
lenPE = len(pe) 

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


with open("pdfpe1.bin", "rb") as f:
  prefix1 = f.read()
with open("pdfpe2.bin", "rb") as f:
  prefix2 = f.read()

assert hashlib.md5(prefix1).hexdigest() == hashlib.md5(prefix2).hexdigest()
assert hashlib.sha1(prefix1).hexdigest() != hashlib.sha1(prefix2).hexdigest()
assert len(prefix1) == len(prefix2)
lenPrefix = len(prefix1)

file1 = prefix1 + cleaned[lenPrefix:]
file2 = prefix2 + cleaned[lenPrefix:]

with open("collision1.pdf", "wb") as f:
  f.write(file1)
with open("collision2.exe", "wb") as f:
  f.write(file2)

os.remove('merged.pdf')
os.remove('hacked.pdf')
os.remove('cleaned.pdf')

md5 = hashlib.md5(file1).hexdigest()

assert md5 == hashlib.md5(file2).hexdigest()

# to prove the files should be 100% valid
print
os.system('mutool info -X collision1.pdf')
print

print
print "MD5: %s" % md5
print "Success!"
