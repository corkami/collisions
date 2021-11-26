#!/usr/bin/env python3

# append a common suffix archive with adjusted timestamps to 2 different files

# MIT Licence - Ange Albertini 2021

import hashlib
import time
import sys
import zipfile as z  # No hack needed
from shutil import copyfile

fn_prefix1, fn_prefix2, fn_suffix = sys.argv[1:4]

copyfile(fn_prefix1, "coll1.zip")
copyfile(fn_prefix2, "coll2.zip")

# adjust time to get some constance - seconds are used as an index
adjust = lambda s, i:[s[0], s[1], s[2], s[3], 9*(s[4]//9), (2*i) % 60]

zp1 = z.ZipFile("coll1.zip", "a")
zp2 = z.ZipFile("coll2.zip", "a")


with z.ZipFile(fn_suffix, "r") as zc:
	print("Suffix: %i file(s)" % len(zc.namelist()))
	for i, fn in enumerate(zc.namelist()):
		adj_time = adjust(time.localtime(time.time())[:6], i)
		zi = z.ZipInfo(fn, date_time=adj_time)
		zi.compress_type = z.ZIP_DEFLATED

		zp1.writestr(zi, zc.open(fn).read())
		zp2.writestr(zi, zc.open(fn).read())

zp1.close()
zp2.close()


with open("coll1.zip", "rb") as f1:	d1 = f1.read()
with open("coll2.zip", "rb") as f2:	d2 = f2.read()

assert d1 != d2
assert len(d1) == len(d2)
assert hashlib.md5(d1).digest() == hashlib.md5(d2).digest()
print("Common md5:", hashlib.md5(d1).hexdigest())
print("Success!")
