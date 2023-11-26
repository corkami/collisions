#!/usr/bin/env python3

DESCRIPTION = "Set rendered hex value in SPQ's 'AVP' GIF hashquine."

# Ange Albertini 2023

from collisions import *
from argparse import ArgumentParser
import random
import hashlib

HEX_BASE = 16
MD5_LEN = 32

HEADER_S = 398016
HEADER_MD5 = "136e622f9d89c84f35729d2354ca3017"

# 512 fastcolls - 1 to display a different nibble - Even nibbles have a longer delay.
block_indexes = [
    1613, 1622, 1632, 1641, 1649, 1658, 1666, 1674, 1683, 1692, 1702, 1711,
    1721, 1730, 1739, 1748, 1757, 1766, 1775, 1783, 1791, 1800, 1809, 1818,
    1828, 1837, 1847, 1855, 1863, 1873, 1882, 1890, 1900, 1909, 1917, 1927,
    1936, 1946, 1955, 1964, 1974, 1982, 1991, 2000, 2009, 2019, 2028, 2037,
    2046, 2055, 2063, 2073, 2081, 2091, 2100, 2108, 2118, 2127, 2135, 2144,
    2154, 2164, 2173, 2182, 2192, 2201, 2209, 2217, 2226, 2234, 2242, 2250,
    2260, 2269, 2277, 2287, 2297, 2305, 2315, 2325, 2334, 2343, 2352, 2361,
    2370, 2379, 2387, 2396, 2405, 2414, 2422, 2430, 2439, 2449, 2459, 2468,
    2478, 2486, 2495, 2505, 2514, 2523, 2531, 2539, 2548, 2557, 2566, 2575,
    2585, 2594, 2604, 2613, 2623, 2631, 2640, 2648, 2657, 2666, 2675, 2683,
    2693, 2701, 2709, 2718, 2728, 2736, 2745, 2753, 2762, 2771, 2781, 2790,
    2799, 2807, 2817, 2827, 2835, 2844, 2852, 2861, 2870, 2879, 2889, 2898,
    2906, 2915, 2924, 2933, 2942, 2951, 2960, 2969, 2978, 2987, 2996, 3005,
    3014, 3023, 3032, 3040, 3049, 3059, 3068, 3076, 3085, 3094, 3103, 3112,
    3122, 3132, 3141, 3150, 3160, 3170, 3179, 3188, 3196, 3205, 3214, 3223,
    3232, 3241, 3251, 3260, 3269, 3278, 3287, 3295, 3304, 3313, 3322, 3330,
    3340, 3349, 3358, 3367, 3375, 3384, 3393, 3402, 3410, 3418, 3427, 3435,
    3445, 3453, 3462, 3470, 3480, 3490, 3499, 3509, 3519, 3528, 3537, 3547,
    3556, 3564, 3573, 3582, 3591, 3600, 3609, 3618, 3627, 3637, 3646, 3654,
    3662, 3670, 3680, 3689, 3698, 3707, 3715, 3724, 3734, 3743, 3752, 3761,
    3770, 3779, 3788, 3797, 3807, 3816, 3825, 3835, 3844, 3853, 3861, 3870,
    3880, 3890, 3898, 3908, 3916, 3925, 3935, 3945, 3954, 3963, 3973, 3981,
    3990, 3999, 4007, 4015, 4024, 4033, 4042, 4052, 4061, 4070, 4078, 4087,
    4096, 4104, 4113, 4121, 4129, 4138, 4147, 4156, 4166, 4175, 4185, 4195,
    4204, 4213, 4222, 4230, 4238, 4248, 4257, 4265, 4274, 4283, 4292, 4300,
    4310, 4319, 4327, 4336, 4346, 4355, 4365, 4375, 4384, 4393, 4403, 4412,
    4421, 4429, 4439, 4447, 4457, 4466, 4475, 4484, 4493, 4502, 4511, 4520,
    4529, 4539, 4549, 4558, 4567, 4577, 4586, 4595, 4604, 4614, 4623, 4632,
    4641, 4650, 4659, 4668, 4676, 4685, 4694, 4702, 4712, 4720, 4728, 4737,
    4746, 4754, 4763, 4772, 4782, 4791, 4799, 4808, 4817, 4827, 4835, 4843,
    4853, 4862, 4871, 4879, 4889, 4899, 4907, 4917, 4925, 4934, 4943, 4952,
    4961, 4970, 4979, 4988, 4997, 5006, 5016, 5026, 5036, 5045, 5054, 5062,
    5070, 5078, 5087, 5096, 5106, 5116, 5125, 5135, 5143, 5152, 5161, 5170,
    5180, 5190, 5199, 5209, 5218, 5227, 5235, 5243, 5252, 5261, 5269, 5278,
    5288, 5296, 5305, 5313, 5322, 5332, 5340, 5350, 5359, 5368, 5377, 5387,
    5396, 5404, 5413, 5422, 5431, 5439, 5448, 5456, 5465, 5475, 5484, 5493,
    5503, 5512, 5521, 5530, 5539, 5548, 5558, 5568, 5577, 5586, 5594, 5603,
    5612, 5620, 5629, 5639, 5648, 5657, 5665, 5673, 5682, 5691, 5700, 5709,
    5718, 5727, 5737, 5746, 5756, 5765, 5775, 5785, 5794, 5802, 5810, 5819,
    5828, 5836, 5846, 5855, 5864, 5872, 5881, 5890, 5900, 5909, 5919, 5928,
    5937, 5946, 5955, 5964, 5972, 5981, 5990, 5999, 6008, 6016, 6025, 6034,
    6043, 6053, 6061, 6070, 6079, 6088, 6097, 6106, 6116, 6125, 6133, 6143,
    6152, 6161, 6170, 6179, 6188, 6197, 6207, 6217
]


def reset(data):
    # manual reset from hashquine file state
    FULL_MD5 = "8895af74c2b5478c547cfb85f7475f0b"

    for letter_index, letter in enumerate(FULL_MD5):
        value = int(letter, HEX_BASE)
        block_index = letter_index * 16 + value
        data, _ = setFastcoll(data, block_indexes[block_index])

    # peeking collision reset state
    reset_sidesB = []
    for block_index in block_indexes:
        _, sideB = setFastcoll(data, block_index)
        if sideB:
            reset_sidesB += [block_index]
    print(reset_sidesB)


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

    assert hashlib.md5(data[:HEADER_S]).hexdigest() == HEADER_MD5
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

    # reset collisions
    for block_index in block_indexes:
        data = setFastCollbySize(data,
                                    block_index,
                                    bSmaller=True,
                                    DIFF_BYTE=0x7B)

    # set value
    for letter_index, letter in enumerate(hex_value):
        value = int(letter, HEX_BASE)
        block_index = letter_index * 16 + value
        data, _ = setFastcoll(data, block_indexes[block_index])

    with open("output.gif", "wb") as f:
        f.write(data)


if __name__ == '__main__':
    main()
