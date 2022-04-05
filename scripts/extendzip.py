#!/usr/bin/env python3

# append a common suffix archive with adjusted timestamps to 2 different files

# MIT Licence - Ange Albertini 2021-2022

import argparse
import hashlib
import io
import time
import sys
import zipfile as z  # No hack needed
from shutil import copyfile
from shutil import move


def extend(prefix, suffix):
	with open("%s1.zip" % prefix, "rb") as f:
		hColl1 = io.BytesIO(f.read())
	with open("%s2.zip" % prefix, "rb") as f:
		hColl2 = io.BytesIO(f.read())

	# adjust time to get some constance - seconds are used as an index
	adjust = lambda s, i:[s[0], s[1], s[2], s[3], 9*(s[4]//9), (2*i) % 60]

	zp1 = z.ZipFile(hColl1, "a")
	zp2 = z.ZipFile(hColl2, "a")

	with z.ZipFile(suffix, "r") as zc:
		print("Suffix: %i file(s)" % len(zc.namelist()))
		for i, fn in enumerate(zc.namelist()):
			adj_time = adjust(time.localtime(time.time())[:6], i)
			zi = z.ZipInfo(fn, date_time=adj_time)
			zi.compress_type = z.ZIP_DEFLATED

			zp1.writestr(zi, zc.open(fn).read())
			zp2.writestr(zi, zc.open(fn).read())

	zp1.close()
	zp2.close()
	return hColl1, hColl2


def checkWrite(prefix, hColl1, hColl2):
	d1 = hColl1.getvalue()
	d2 = hColl2.getvalue()

	assert len(d1) == len(d2)
	assert d1 != d2
	assert hashlib.md5(d1).digest() == hashlib.md5(d2).digest()

	print("Common md5:", hashlib.md5(d1).hexdigest())
	print("Success!")

	hex = hashlib.md5(d1).hexdigest().upper()
	with open("coll1-%s.%s" % (hex[:8], prefix), "wb") as f: f.write(d1)
	with open("coll2-%s.%s" % (hex[:8], prefix), "wb") as f: f.write(d2)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Generic collision of zip+xml file formats.")

	parser.add_argument('prefix', help="prefix name (files should be colled <prefix>1.zip and <prefix>2.zip.")
	parser.add_argument('suffix', help="Second prefix file.")
	args = parser.parse_args()
	prefix = args.prefix
	suffix = args.suffix

	hColl1, hColl2 = extend(prefix, suffix)
	checkWrite(prefix, hColl1, hColl2)
