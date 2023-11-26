#!/usr/bin/env python3

DESCRIPTION = "Set rendered hex value in Mako's JPG+PDF hashquine."

# Ange Albertini 2023

from collisions import setFastCollbySize
from argparse import ArgumentParser
import random
import hashlib

HEX_BASE = 16
MD5_LEN = 32

HEADER_S = 0x140
MD5_HEADER = "d43cd6b1241cd3e9c5ed237da1656ef3"

# index of the 2nd fastcoll block
block_indexes = [
    6, 17, 28, 39, 50, 62, 74, 86, 98, 110, 121, 133, 144, 156, 168, 196, 206,
    217, 229, 240, 251, 261, 273, 283, 294, 305, 317, 329, 341, 352, 386, 397,
    408, 419, 430, 442, 453, 465, 477, 488, 500, 511, 523, 535, 547, 576, 588,
    600, 612, 623, 634, 645, 655, 667, 679, 690, 701, 713, 725, 737, 767, 779,
    790, 802, 814, 826, 837, 847, 859, 871, 883, 895, 907, 919, 931, 957, 968,
    980, 991, 1003, 1014, 1025, 1037, 1049, 1061, 1072, 1084, 1095, 1106, 1117,
    1147, 1158, 1170, 1180, 1190, 1201, 1213, 1223, 1234, 1246, 1258, 1270,
    1281, 1292, 1303, 1337, 1349, 1361, 1372, 1384, 1396, 1408, 1420, 1431,
    1442, 1453, 1465, 1476, 1487, 1498, 1527, 1538, 1550, 1561, 1572, 1583,
    1595, 1607, 1618, 1629, 1640, 1651, 1663, 1674, 1686, 1718, 1730, 1742,
    1754, 1765, 1776, 1788, 1799, 1810, 1822, 1833, 1845, 1857, 1869, 1881,
    1908, 1920, 1931, 1943, 1955, 1967, 1977, 1989, 2001, 2013, 2025, 2036,
    2048, 2060, 2070, 2098, 2110, 2121, 2132, 2143, 2154, 2166, 2177, 2189,
    2201, 2212, 2224, 2236, 2248, 2260, 2288, 2299, 2310, 2321, 2332, 2344,
    2355, 2367, 2379, 2390, 2401, 2413, 2425, 2437, 2449, 2479, 2491, 2503,
    2514, 2525, 2537, 2549, 2560, 2572, 2583, 2595, 2607, 2619, 2630, 2641,
    2669, 2680, 2691, 2702, 2713, 2724, 2736, 2747, 2758, 2768, 2779, 2790,
    2800, 2811, 2823, 2859, 2871, 2883, 2894, 2906, 2918, 2929, 2941, 2952,
    2964, 2976, 2987, 2998, 3010, 3021, 3049, 3061, 3072, 3083, 3095, 3106,
    3117, 3128, 3140, 3150, 3160, 3171, 3183, 3195, 3206, 3239, 3251, 3261,
    3272, 3283, 3294, 3305, 3316, 3327, 3339, 3351, 3363, 3375, 3386, 3398,
    3430, 3442, 3453, 3465, 3475, 3487, 3499, 3511, 3523, 3534, 3545, 3556,
    3568, 3580, 3591, 3620, 3632, 3642, 3654, 3666, 3677, 3687, 3699, 3710,
    3722, 3734, 3745, 3756, 3767, 3778, 3810, 3822, 3834, 3846, 3857, 3869,
    3881, 3893, 3904, 3915, 3927, 3938, 3950, 3961, 3972, 4000, 4011, 4023,
    4034, 4045, 4056, 4068, 4079, 4090, 4100, 4112, 4123, 4135, 4146, 4158,
    4191, 4202, 4213, 4224, 4236, 4248, 4260, 4272, 4284, 4296, 4308, 4320,
    4331, 4343, 4353, 4381, 4391, 4403, 4415, 4427, 4439, 4450, 4462, 4474,
    4486, 4498, 4510, 4522, 4534, 4546, 4571, 4582, 4593, 4604, 4616, 4626,
    4637, 4649, 4661, 4672, 4684, 4694, 4706, 4717, 4729, 4761, 4773, 4785,
    4796, 4808, 4820, 4832, 4844, 4855, 4866, 4878, 4889, 4900, 4912, 4924,
    4952, 4964, 4975, 4986, 4998, 5009, 5021, 5033, 5044, 5056, 5067, 5078,
    5089, 5101, 5113, 5142, 5154, 5165, 5176, 5186, 5197, 5209, 5221, 5233,
    5244, 5254, 5266, 5278, 5289, 5301, 5332, 5342, 5354, 5365, 5377, 5388,
    5399, 5411, 5423, 5434, 5446, 5458, 5468, 5480, 5492, 5522, 5534, 5546,
    5558, 5569, 5581, 5593, 5605, 5616, 5626, 5638, 5650, 5662, 5673, 5685,
    5713, 5724, 5734, 5744, 5754, 5766, 5778, 5790, 5802, 5814, 5826, 5838,
    5850, 5861, 5872, 5903, 5913, 5924, 5936, 5948, 5960, 5971, 5982, 5994,
    6005, 6017, 6029, 6041, 6053, 6064
]


def reset(input):
    MD5_FULL = "71aa13f4b83b424807e3db3260ffe20b"
    output = bytearray(input)
    if hashlib.sha1(
            output).hexdigest() == "7c2de0f18535ea4cc69780ac16df1c5f65ae79e9":
        print('Hasquine configuration found, resetting')
        for i, c in enumerate(MD5_FULL):

            v = int(c, HEX_BASE)
            if v < 15:
                output, _ = setFastcoll(output, block_indexes[i * 15 + v] - 1)
        for i, idx in enumerate(block_indexes):
            output, _ = setFastcoll(output, idx - 1)

    # At this point, we should have a reset file.
    assert hashlib.sha1(
        output).hexdigest() == "721d74e9b486b567da6c1986678e9ab61f690182"
    return output


def getSides(data):
    sides = []
    for i, idx in enumerate(block_indexes):
        _, sideB = setFastcoll(data, idx - 1)
        if sideB:
            sides += [i]
    return sides


def main():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-v',
                        '--value',
                        type=str,
                        nargs='?',
                        const=random,
                        help='Hex value to encode (random if not specified)')

    parser.add_argument("filename")
    args = parser.parse_args()

    fn = args.filename
    with open(fn, "rb") as f:
        data = bytearray(f.read())

    # check we have the right file
    assert hashlib.md5(data[:HEADER_S]).hexdigest() == MD5_HEADER

    if args.value is not None:
        if args.value == random:
            hex_value = "".join(
                [random.choice("0123456789abcdef") for _ in range(MD5_LEN)])
            print("Encoding random value: %s" % hex_value)
        else:
            hex_value = "%032x" % int(args.value, HEX_BASE)
            hex_value = hex_value[:MD5_LEN]
            print("Encoding requested value: `%s` (len:%i)" %
                  (hex_value, len(hex_value)))
    else:
        hex_value = hashlib.md5(data).hexdigest()
        print("Encoding file MD5: `%s` (len:%i)" % (hex_value, len(hex_value)))

    # set the actual value
    for char_index, char in enumerate(hex_value):
        v = int(char, HEX_BASE)
        for j in range(15):
            idx = char_index * 15 + j
            data = setFastCollbySize(data,
                                     block_indexes[idx] - 1,
                                     bSmaller=(j < v))

    with open("output.pdf", "wb") as f:
        f.write(data)


if __name__ == '__main__':
    main()
