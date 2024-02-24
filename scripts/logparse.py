#!/usr/bin/env python3

# A detectcoll log parser with collision signatures
# based on message and intermediate hash values differentials

# usage detectcoll <file> | logparse.py

# Ange Albertini 2024
# With the help of Marc Stevens

import sys

# Warning: there could be... collisions (!) in dIhv sigs.
sigs = {  # dMsg, dIhv
    "APop": ["", "31,31,31,31"],
    "FastColl": ["4,11,14", "31,31,25,31,25,31,25"],
    "Flame": ["4,11,14", "31,31,30,24,23,13,12,7,4,3,1,31,25,14,9,31,25,9"],
    "Unicoll1": ["2", "31,31,23,31,23,31"],
    "Unicoll2": ["0,6,13", None],
    "Unicoll3": ["6,9,15", '31,23,31,23,1,31,23,1,31,23,1'],
    "HashClashCPC": ["11", None],
    "SingleCPC": ["2,4,11,14", None],
    "SingleIPC": ["8,13", ""],
    "SHAttered/Shambles": ["0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15", None],
}


def make_dihv_sig(ihv1: str, ihv2: str) -> str:
    indexes = []
    for index in range(0, len(ihv1), 8):
        x = (int(ihv1[index: index+8], 16) -
             int(ihv2[index: index+8], 16)) % 2**32
        x1 = format(x >> 1, '032b')
        x2 = format((x >> 1) + x, '032b')
        for index, char in enumerate(x1):
            if char != x2[index]:
                indexes += [str(31-index)]

    result = ",".join(indexes)
    return result


def make_dm_sig(dms: list) -> str:
    return ",".join([dm.split("=")[0][2:] for dm in dms])


def match_sig(blockNb: int, sig_dms: str, dihv_sig: str) -> None:
    for sig in sigs:
        if (sigs[sig][0] == sig_dms):
            if (sigs[sig][1] is None) or ((sigs[sig][1] is not None) and sigs[sig][1] == dihv_sig):
                print(f"block: {blockNb}, collision: {sig}")
                return
    else:
        print("Nothing found:", repr(dihv_sig), repr(sig_dms))
    return


def main():
    step = 0
    ihv1 = None
    ihv2 = None
    dms = None
    blockNb = None

    for line in sys.stdin:
        line = line.strip()
        if (step == 0) and (line.startswith('Found collision in block ')):
            block_s = line.split(" ")[4]
            if block_s.endswith(":"):  # Sha1 blocks have more information
                block_s = block_s[:-1]
            blockNb = int(block_s)
            step = 1

        elif (step == 1) and (line.startswith('dm:')):
            dms = line.split(" ")[1:]
            dm_sig = make_dm_sig(dms)
            step = 2

        elif (step == 2) and (line.startswith('ihv1')):
            _, ihv1 = line.split("=")
            assert len(ihv1) % 8 == 0
            step = 3

        elif (step == 3) and (line.startswith('ihv2')):
            _, ihv2 = line.split("=")
            assert len(ihv2) == len(ihv1)
            dihv_sig = make_dihv_sig(ihv1, ihv2)

            match_sig(blockNb, dm_sig, dihv_sig)
            step = 0


if __name__ == '__main__':
    main()
