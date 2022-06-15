#!/usr/bin/env python3

# Zinsider: instant md5 collisions of pairs of zip+xml files

# Ange Albertini 2022 - MIT licence

# Office Open XML: docx / pptx / xlsx
# Open Container Format: epub
# Open Packaging Conventions:
# - 3D manufacturing format: 3mf
# - XML Paper Specification: xps / oxps

import extendzip

import argparse
import io
import os.path
import sys
import xml.etree.ElementTree as ET
import zipfile as ZF


def getArgs():
	parser = argparse.ArgumentParser(description="Generate MD5 collisions of zip+xml file formats.")

	parser.add_argument('file1', help="First input file.")
	parser.add_argument('file2', help="Second input file.")

	args = parser.parse_args()
	return args


def getFileType(zip):
	filelist = zip.namelist()
	if "FixedDocumentSequence.fdseq" in filelist:
		return "oxps"
	if "FixedDocSeq.fdseq" in filelist:
		return "xps"
	if "word/document.xml" in filelist:
		return "docx"
	if "xl/workbook.xml" in filelist:
		return "xlsx"
	if "ppt/presentation.xml" in filelist:
		return "pptx"
	if "EPUB/package.opf" in filelist:
		return "epub"
	if "3D/3dmodel.model" in filelist:
		return "3mf"
	return None


def checkFileType(zip1, zip2):
	type1 = getFileType(zip1)

	if type1 is None:
		print("Error: unknown file type: '%s'" % os.path.basename(fn1))
		sys.exit()

	type2 = getFileType(zip2)

	if type2 is None:
		print("Error: unknown file type: '%s'" % os.path.basename(fn2))
		sys.exit()

	if type1 != type2:
		print("Error: file types not matching: '%s' - '%s'" % (os.path.basename(fn1),os.path.basename(fn2)))
		sys.exit()
	return type1


def appendNumber(p, suffix="1", skip=1):
	# absolute paths start with a `/` that should be left unchanged
	return p[:skip] + p[skip:].replace("/", suffix+"/", 1)


def replaceNumber(p, suffix="1", skip=1):
	# absolute paths start with a `/` that should be left unchanged
	return p[:skip] + p[skip:].replace("1/", suffix+"/", 1)


def setParams(comtype):
	global updatePath, REL_FN, MOVE_EXCL, ATTRIB, XPATH, BLOCKS, CONTENT_FN
	if comtype in ["docx", "xlsx", "pptx", "3mf"]:
		REL_FN = "_rels/.rels" # ".//{http://schemas.openxmlformats.org/package/2006/relationships}Relationship[@Target]",
		ET.register_namespace('', 'http://schemas.openxmlformats.org/package/2006/content-types')
		CONTENT_FN = "[Content_Types].xml"
		MOVE_EXCL = "docProps/"
		ATTRIB = 'PartName'
		XPATH = ".//{http://schemas.openxmlformats.org/package/2006/content-types}Override[@PartName]"
		BLOCKS = ET.Element("Override",
					attrib={"PartName":"/blocks", "ContentType":"application/octet-stream"})

	elif comtype == "epub":
		REL_FN = "META-INF/container.xml" # ".//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile[@full-path]"
		ET.register_namespace('', 'urn:oasis:names:tc:opendocument:xmlns:container')

	elif comtype == "xps":
		REL_FN = "FixedDocSeq.fdseq" # //{http://schemas.microsoft.com/xps/2005/06}DocumentReference[@Source]"
		ET.register_namespace('', 'http://schemas.microsoft.com/xps/2005/06')
		MOVE_EXCL = "_rels/"
		updatePath = replaceNumber

	elif comtype == "oxps":
		REL_FN = "FixedDocumentSequence.fdseq" # //{http://schemas.openxps.org/oxps/v1.0}DocumentReference[@Source]"
		ET.register_namespace('', 'http://schemas.openxps.org/oxps/v1.0')
		MOVE_EXCL = "_rels/"
		updatePath = replaceNumber
	else:
		print("Error !")
		sys.exit()


def mergeZips():
	for iz in zip1.infolist():
		data_ = zip1.read(iz)

		if iz.filename in [REL_FN, CONTENT_FN]:
			continue

		np = iz.filename
		if not np.startswith(MOVE_EXCL):
			np = updatePath(np, suffix="1")
		# print("> %s => %s" % (iz.filename, np))
		iz.filename = np
		zfSuffix.writestr(iz, data_)

	for iz in zip2.infolist():
		data_ = zip2.read(iz)

		if iz.filename in [REL_FN, CONTENT_FN]:
			continue

		np = iz.filename
		if not np.startswith(MOVE_EXCL):
			np = updatePath(np, suffix="2")
		# print("> %s => %s" % (iz.filename, np))
		iz.filename = np
		# Skip duplicate
		if iz.filename in zip1.namelist():
			# print("File already existing:", iz.filename)
			continue
		zfSuffix.writestr(iz, data_)


def mergeCT():
	if CONTENT_FN is not None:
		print("Copying content types")
		tree = ET.ElementTree()
		treeExtra = ET.ElementTree()

		filename = CONTENT_FN
		tree.parse(zip1.open(filename))
		root = tree.getroot()

		for e in root.findall(XPATH):
			a = e.attrib[ATTRIB]
			if not (a.startswith(MOVE_EXCL) or 
				a.startswith("/" + MOVE_EXCL)):
				na = updatePath(a, suffix="1")
				e.attrib[ATTRIB] = na
				# print("> Content types(1):", a, na)

		# Getting all paths
		attribs1 = [e.attrib[ATTRIB] for e in root.findall(XPATH)]

		print("Merging content types")
		treeExtra.parse(zip2.open(filename))
		rootExtra = treeExtra.getroot()

		for e in rootExtra.findall(XPATH):
			a = e.attrib[ATTRIB]
			if not (a.startswith(MOVE_EXCL) or 
				a.startswith("/" + MOVE_EXCL)):
				na = updatePath(a, suffix="2")
				e.attrib[ATTRIB] = na
				# print("> Content types(2):", a, na)
			# avoid duplicates
			if e.attrib[ATTRIB] not in attribs1:
				root.append(ET.Element(
					e.tag, e.attrib
					))

		if BLOCKS is not None:
			print("Adding collision block exclusion")
			root.append(BLOCKS)
	
		if sys.version_info >= (3,9):
			ET.indent(tree, space="\t", level=0)

		data_ = ET.tostring(root, encoding='utf-8', xml_declaration=True)
		zfSuffix.writestr(filename, data_)


if __name__ == '__main__':
	args = getArgs()
	zip1 = ZF.ZipFile(args.file1)
	zip2 = ZF.ZipFile(args.file2)

	comtype = checkFileType(zip1, zip2)

	print("Common file type: %s" % (comtype))

	# XML Manifest pointing to root file.
	REL_FN = None

	# Directory not to be moved - 'docProps/' in office file.
	MOVE_EXCL = "\x00"

	# Content type XML file that needs path updating
	CONTENT_FN = None
	XPATH = None
	ATTRIB = None
	# XML element to be added to content type to hide collision blocks
	BLOCKS = None

	updatePath = appendNumber

	setParams(comtype)

	hSuffix = io.BytesIO()
	with ZF.ZipFile(hSuffix, mode='w') as zfSuffix:
		print("Merging archived files")
		mergeZips()
		mergeCT()

	print("Merging suffix with prefix pair")
	hColl1, hColl2 = extendzip.extend(comtype, hSuffix)
	print("Verifying and saving")
	extendzip.checkWrite(comtype, hColl1, hColl2)
