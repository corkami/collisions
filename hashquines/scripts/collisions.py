#!/usr/bin/env python3

# Flip or reset collision blocks for Unicoll or Fastcoll

# Ange Albertini 2022-2023

import hashlib

BLOCK_SIZE = 0x40


def read_dword(data: bytearray, offset: int):
    return int.from_bytes(data[offset:offset + 4], "little")


def write_dword(data: bytearray, value: int, offset: int):
    for i in range(4):
        data[offset + i] = (value >> (i * 8)) & 0xFF
    return data


def setFastCollbySize(data: bytearray, block_idx: int, bSmaller=True, DIFF_BYTE=0x3b):
    """Set a FastColl depending on the size (small or big)
    of a byte value encoded at a specific offset
    """
    XOR_MASK = 0x80
    XOR_OFFSETS = [0x13, 0x3b]
    assert DIFF_BYTE in [
        0x13, 0x2D, 0x3B,
        0x40 + 0x13, 0x40 + 0x2D, 0x40 + 0x3B,
    ]
    block_off = block_idx * BLOCK_SIZE
    assert block_off + 0x80 <= len(data)
    md5_old = hashlib.md5(data).hexdigest()
    data_old = bytearray(data)
    data_new = bytearray(data)

    for offset in XOR_OFFSETS:
        data_new[block_off + offset] = XOR_MASK ^ data_new[block_off + offset]
        offset += BLOCK_SIZE
        data_new[block_off + offset] = XOR_MASK ^ data_new[block_off + offset]

    dword1_1 = read_dword(data_new, block_off + 0x2c)
    dword1_2 = read_dword(data_new, block_off + 0x6c)

    # from File2 to File1
    dword2_1 = dword1_1 + 0x8000
    dword2_2 = dword1_2 - 0x8000
    data_new = write_dword(data_new, dword2_1, 0x2c + block_off)
    data_new = write_dword(data_new, dword2_2, 0x2c + block_off + BLOCK_SIZE)
    if hashlib.md5(data_new).hexdigest() == md5_old:
        data1 = data_new
        data2 = data_old
    else:
        # didn't work? Do it the other way around
        dword2_1 = dword1_1 - 0x8000
        dword2_2 = dword1_2 + 0x8000
        data_new = write_dword(data_new, dword2_1, 0x2c + block_off)
        data_new = write_dword(data_new, dword2_2,
                               0x2c + block_off + BLOCK_SIZE)
        data1 = data_old
        data2 = data_new

    assert hashlib.md5(data1).hexdigest() == md5_old
    assert hashlib.md5(data2).hexdigest() == md5_old

    assert data1[block_off + DIFF_BYTE] != (data2[block_off + DIFF_BYTE])

    return data1 if bSmaller == (data1[block_off + DIFF_BYTE] < (data2[block_off + DIFF_BYTE])) else data2


def setFastcoll(data: bytearray, block_idx: int, sideB: bool = None):
    """Set a given 'side' of FastColl (False = left, True = right)
    Get the other side of the collision if no side if specified
    """
    XOR_MASK = 0x80
    XOR_OFFSETS = [0x13, 0x3b]
    block_off = block_idx * BLOCK_SIZE
    assert block_off + 0x80 <= len(data)
    md5_old = hashlib.md5(data).hexdigest()
    data_old = bytearray(data)
    data_new = bytearray(data)

    for offset in XOR_OFFSETS:
        data_new[block_off + offset] = XOR_MASK ^ data_new[block_off + offset]
        offset += BLOCK_SIZE
        data_new[block_off + offset] = XOR_MASK ^ data_new[block_off + offset]

    dword1_1 = read_dword(data_new, block_off + 0x2c)
    dword1_2 = read_dword(data_new, block_off + 0x6c)

    # from File2 to File1
    dword2_1 = dword1_1 + 0x8000
    dword2_2 = dword1_2 - 0x8000
    data_new = write_dword(data_new, dword2_1, 0x2c + block_off)
    data_new = write_dword(data_new, dword2_2, 0x2c + block_off + BLOCK_SIZE)
    if hashlib.md5(data_new).hexdigest() == md5_old:
        foundSizeB = True
        data1 = data_new
        data2 = data_old
    else:
        # didn't work? Do it the other way around
        foundSizeB = False
        dword2_1 = dword1_1 - 0x8000
        dword2_2 = dword1_2 + 0x8000
        data_new = write_dword(data_new, dword2_1, 0x2c + block_off)
        data_new = write_dword(data_new, dword2_2,
                               0x2c + block_off + BLOCK_SIZE)
        data1 = data_old
        data2 = data_new

    assert hashlib.md5(data1).hexdigest() == md5_old
    assert hashlib.md5(data2).hexdigest() == md5_old

    # return the specified side if any
    if sideB is None:
        return data_new, foundSizeB
    if sideB == False:
        return data1, foundSizeB
    elif sideB == True:
        return data2, foundSizeB


def getFastColls(data: bytearray):
    BLOCK_SIZE = 0x40
    l = len(data)
    block_count = (l - l % BLOCK_SIZE) // BLOCK_SIZE
    indexes = []
    sidesB = []  # type: list[int]
    for i in range(block_count):
        try:
            _, sideB = setFastcoll(data, i)
        except AssertionError:
            continue
        indexes += [i]
        if sideB:
            sidesB += [i]
    return indexes, sidesB


def add4(data, offset, operand):
    value = int.from_bytes(data[offset:offset + 4], "little")
    value += operand
    value %= 0x100000000
    return data[:offset] + value.to_bytes(4, "little") + data[offset + 4:]


def setUniColl(data: bytearray, block_idx: int, sideB: bool = None):
    # get a given 'side' of a Unicoll (False = left, True = right)
    # Get the other side of the collision if no side if specified

    # That's UniColl #1 btw
    OFFSET = +8
    DELTA = 0x100

    block_off = block_idx * BLOCK_SIZE
    assert block_off + 0x80 <= len(data)
    md5_old = hashlib.md5(data).hexdigest()
    data_old = bytearray(data)

    # File2 to File1 ?
    data_new = add4(data_old, block_off + OFFSET, DELTA)
    data_new = add4(data_new, block_off + OFFSET + BLOCK_SIZE, -DELTA)
    if hashlib.md5(data_new).hexdigest() == md5_old:
        foundSizeB = True
        data1 = data_new
        data2 = data_old
    else:
        # File1 to File 2 ?
        foundSizeB = False
        data_new = add4(data_old, block_off + OFFSET, -DELTA)
        data_new = add4(data_new, block_off + OFFSET + BLOCK_SIZE, +DELTA)
        data1 = data_old
        data2 = data_new

    assert hashlib.md5(data1).hexdigest() == md5_old
    assert hashlib.md5(data2).hexdigest() == md5_old

    # return the specified side if any
    if sideB is None:
        return data_new, foundSizeB
    if sideB == False:
        return data1, foundSizeB
    elif sideB == True:
        return data2, foundSizeB


def getUniColls(data: bytearray):
    BLOCK_SIZE = 0x40
    l = len(data)
    block_count = (l - l % BLOCK_SIZE) // BLOCK_SIZE
    indexes = []
    sidesB = []  # type: list[int]
    for i in range(block_count):
        try:
            _, sideB = setUniColl(data, i)
        except AssertionError:
            continue
        indexes += [i]
        if sideB:
            sidesB += [i]
    return indexes, sidesB
