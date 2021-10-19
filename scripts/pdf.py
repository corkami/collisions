#!/usr/bin/env python3

# script to craft MD5 collisions of 2 PDFs via mutool and UniColl

# Ange Albertini 2018-2021

# uses mutool from https://mupdf.com/index.html

import os
import sys
import hashlib


MUTOOL = "mutool.exe"

def EnclosedString(d, starts, ends):
  off = d.find(starts) + len(starts)
  return d[off:d.find(ends, off)]

def getCount(d):
  s = EnclosedString(d, b"/Count ", b"/")
  count = int(s)
  return count

def procreate(l): # :p
  return b" 0 R ".join(l) + b" 0 R"

def adjustPDF(contents):
  """dumb [start]xref fix: fixes old-school xref with no holes, with hardcoded \\n"""
  startXREF = contents.find(b"\nxref\n0 ") + 1
  endXREF = contents.find(b" \n\n", startXREF) + 1
  origXref = contents[startXREF:endXREF]
  objCount = int(origXref.splitlines()[1].split(b" ")[1])
  print("object count: %i" % objCount)

  xrefLines = [
    b"xref",
    b"0 %i" % objCount,
    # mutool declare its first xref like this
    b"0000000000 00001 f "
    ]

  i = 1
  while i < objCount:
    # doesn't support comments at the end of object declarations
    off = contents.find(b"\n%i 0 obj\n" % i) + 1
    xrefLines.append(b"%010i 00000 n " % (off))
    i += 1

  xref = b"\n".join(xrefLines)

  # XREF length should be unchanged
  try:
    assert len(xref) == len(origXref)
  except AssertionError:
    print("<:", repr(origXref))
    print(">:", repr(xref))

  contents = contents[:startXREF] + xref + contents[endXREF:]

  startStartXref = contents.find(b"\nstartxref\n", endXREF) + len(b"\nstartxref\n")
  endStartXref = contents.find(b"\n%%%%EOF", startStartXref)
  contents = contents[:startStartXref] + "%i" % startXREF + contents[endStartXref:]

  return contents


if len(sys.argv) == 1:
  print("PDF MD5 collider")
  print("Usage: pdf.py <file1.pdf> <file2.pdf>")
  sys.exit()

os.system(MUTOOL + ' merge -o first.pdf %s' % sys.argv[1])
os.system(MUTOOL + ' merge -o second.pdf %s' % sys.argv[2])
os.system(MUTOOL + ' merge -o merged.pdf dummy.pdf %s %s' % (sys.argv[1], sys.argv[2]))

with open("first.pdf", "rb") as f:
  d1 = f.read()

with open("second.pdf", "rb") as f:
  d2 = f.read()

with open("merged.pdf", "rb") as f:
  dm = f.read()


COUNT1 = getCount(d1)
COUNT2 = getCount(d2)


kids = EnclosedString(dm, b"/Kids[", b"]")

# we skip the first dummy, and the last " 0 R" string
pages = kids[:-4].split(b" 0 R ")[1:]

template = b"""%%PDF-1.4

1 0 obj
<<
  /Type /Catalog

  %% for alignments (comments will be removed by merging or cleaning)
  /MD5_is__ /REALLY_dead_now__
  /Pages 2 0 R
  %% to make sure we don't get rid of the other pages when garbage collecting
  /Fakes 3 0 R
  %% placeholder for UniColl collision blocks
  /0123456789ABCDEF0123456789ABCDEF012
  /0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0
>>
endobj

2 0 obj
<</Type/Pages/Count %(COUNT2)i/Kids[%(KIDS2)s]>>
endobj 

3 0 obj
<</Type/Pages/Count %(COUNT1)i/Kids[%(KIDS1)s]>>
endobj

%% overwritten - was a fake page to fool merging
4 0 obj
<< >>
endobj

"""

KIDS1 = procreate(pages[:getCount(d1)])

KIDS2 = procreate(pages[getCount(d1):])

contents = template % locals()

# adjust parents for the first set of pages
contents += dm[dm.find(b"5 0 obj"):].replace(b"/Parent 2 0 R", b"/Parent 3 0 R", COUNT1)

# not necessary (will be fixed by mutool anyway) but avoids warnings
contents = adjustPDF(contents)

with open("hacked.pdf", "wb") as f:
  f.write(contents)

# let's adjust offsets - -g to get rid of object 4 by garbage collecting
os.system(MUTOOL + ' clean -gggg hacked.pdf cleaned.pdf')

with open("cleaned.pdf", "rb") as f:
  cleaned = f.read()

# some mutool versions do different stuff :(
cleaned = cleaned.replace(
  b" 65536 f \n0000000016 00000 n \n",
  b" 65536 f \n0000000018 00000 n \n",
  1)

with open("pdf1.bin", "rb") as f:
  prefix1 = f.read()

with open("pdf2.bin", "rb") as f:
  prefix2 = f.read()

file1 = prefix1 + b"\n" + cleaned[192:]
file2 = prefix2 + b"\n" + cleaned[192:]

with open("collision1.pdf", "wb") as f:
  f.write(file1)

with open("collision2.pdf", "wb") as f:
  f.write(file2)

os.remove('first.pdf')
os.remove('second.pdf')
os.remove('merged.pdf')
os.remove('hacked.pdf')
os.remove('cleaned.pdf')

md5 = hashlib.md5(file1).hexdigest()

assert md5 == hashlib.md5(file2).hexdigest()

# to prove the files should be 100% valid
print()
os.system(MUTOOL + ' info -X collision1.pdf')
print()
print()
os.system(MUTOOL + ' info -X collision2.pdf')

print()
print("MD5: %s" % md5)
print("Success!")
