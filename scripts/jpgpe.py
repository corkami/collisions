#!/usr/bin/env python

# moves the PE header right after the prefix, add padding,
# extend header, add remaining JPG data at 0x500,
# adjust section table

# TODO: support 64 bits PE

# hardcoded in the JPG prefix to cover most PE headers
JPGSTART = 0x500

import sys, struct
fnEXE, fnJPG = sys.argv[1:3]

with open("jpg-pe.exe", "rb") as f:
  prefExe = f.read()

with open(fnEXE, "rb") as f:
  Exe = f.read()
assert Exe.startswith("MZ")

with open("jpg-pe.jpg", "rb") as f:
  prefJPG = f.read()

with open(fnJPG, "rb") as f:
  JPG = f.read()
assert JPG.startswith("\xff\xd8")

JPG = JPG[2:]

peHDR = Exe[:JPGSTART].strip("\0")
peHDR = peHDR[peHDR.find("PE\0\0"):]

NumSec = struct.unpack("h", peHDR[0x6:0x6+2])[0]
BaseOfCode = struct.unpack("l", peHDR[0x2c:0x2c+4])[0]
FileAlig = struct.unpack("l", peHDR[0x3c:0x3c+4])[0]
NumDir = struct.unpack("l", peHDR[0x74:0x74+4])[0]

print "%s :" % fnEXE
print " # Sections: %i" % NumSec
print " BaseOfCode: %xh" % BaseOfCode
print " File Alignment: %xh" % FileAlig
print " # DataDirectories: %i" % NumDir

lenJPG = len(JPG)
print "JPG length: %i" % lenJPG

NewOffset = (((lenJPG + 0x500)/FileAlig + 1) * FileAlig)
print "new header length: %xh" % NewOffset

Delta = NewOffset - BaseOfCode
print "Delta: %08xh" % Delta

# get offset of Section Table
TableOff = 0x78 + NumDir * 8

for i in range(NumSec):
  offset = TableOff + i*0x28 + 0x14
  PhysOffset = struct.unpack("l", peHDR[offset:offset+4])[0]
  peHDR = "".join([
    peHDR[:offset],
    struct.pack("l", PhysOffset + Delta),
    peHDR[offset+4:]
    ])
  print " %i: %08xh" % (i + 1, PhysOffset + Delta)


suffix = "".join([
    peHDR,
    (JPGSTART - len(prefExe) - len(peHDR)) * "\0",
    JPG,
    (NewOffset - (lenJPG + JPGSTART)) * "\0",
    Exe[BaseOfCode:]
  ])

with open("collision.exe", "wb") as f:
  f.write(prefExe + suffix)
with open("collision.jpg", "wb") as f:
  f.write(prefJPG + suffix)
