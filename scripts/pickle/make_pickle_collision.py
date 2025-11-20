#!/usr/bin/env python3

import argparse
import os
import sys
import hashlib
import pickle
import pickletools

def parse_args():
    parser = argparse.ArgumentParser(
        description='Process collision blocks and pickle files',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Collision block arguments
    parser.add_argument('-c1', '--collision_blocks1',
                      help='Path to first collision block file (default: collision_blocks1.bin)',
                      default='collision_blocks1.bin')
    parser.add_argument('-c2', '--collision_blocks2',
                      help='Path to second collision block file (default: collision_blocks2.bin)',
                      default='collision_blocks2.bin')
    
    # Pickle file arguments
    parser.add_argument('-f1', '--file1',
                      help='Path to first pickle file',
                      required=True)
    parser.add_argument('-f2', '--file2',
                      help='Path to second pickle file',
                      required=True)

    # Output file arguments
    parser.add_argument('-o1', '--output1',
                      help='Path to first output pickle file',
                      default='colliding_pickle1.pkl')
    parser.add_argument('-o2', '--output2',
                      help='Path to second output pickle file',
                      default='colliding_pickle2.pkl')
    
    args = parser.parse_args()
    
    # Check if default collision block files exist
    if (args.collision_blocks1 == 'collision_blocks1.bin' and not os.path.exists(args.collision_blocks1)) or \
       (args.collision_blocks2 == 'collision_blocks2.bin' and not os.path.exists(args.collision_blocks2)):
        print("Warning: Default collision block file(s) not found. Please specify them using -c1 and -c2 flags.")
        sys.exit(1)
    
    # Check if specified files exist
    for file_path in [args.collision_blocks1, args.collision_blocks2, args.file1, args.file2]:
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} not found.")
            sys.exit(1)
    
    return args

def read_binary_file(file_path):
    with open(file_path, 'rb') as f:
        return f.read()


args = parse_args()

collision_blocks1 = read_binary_file(args.collision_blocks1)
collision_blocks2 = read_binary_file(args.collision_blocks2)

assert len(collision_blocks1) == 2 * 64, "Collision block 1 must be 128 bytes"
assert len(collision_blocks2) == 2 * 64, "Collision block 2 must be 128 bytes"
    
pickle_file1 = read_binary_file(args.file1)
pickle_file2 = read_binary_file(args.file2)

# strip of the first 2 bytes (\x80 \x04 - protocol declaration)
pickle_file1 = pickle_file1[2:]
pickle_file2 = pickle_file2[2:]

print(f"File1 size: {len(pickle_file1)} bytes")
print(f"File2 size: {len(pickle_file2)} bytes")

jumpover_len = 0x174 - 0x074 + len(pickle_file1) - 4 - 1
print(f"Jumpover length: {jumpover_len} bytes")

# add the fake comment chunk
# it is made of the BINBYTE (\x42 = 'B') opcode and a 4-byte little-endian integer denoting its length
skip_block = b'\x42' + jumpover_len.to_bytes(4, byteorder='little')
# at this point, we have 11 bytes remaining on this line, so fill with '!'
skip_block += b'\x21' * 11

ascii_art = b"""
################
#YOU_HAVE_BEEN_#
#PWNED_BY_JAKUB#
#KRYS_AS_PART__#
#OF_THE_AI_SECU#
#RITY_BOOTCAMP_#
#2025_IN_LONDON#
#NOW_ADMIRE_THE#
#BEAUTY_OF_REUS#
#ABLE_HASH_COLL#
#ISIONS_HAHAHA!#
#--------------#
#CREDIT_TO_ANGE#
#ALBERTINI_____#
################
""".replace(b"\n", b"").replace(b"\r", b"")

assert len(ascii_art) == 15 * 16, "ASCII art must be 15x16 bytes"

skip_block += ascii_art

# now combine the skip block with the two pickle files
appendix = skip_block + pickle_file1 + pickle_file2

colliding_pickle1 = collision_blocks1 + appendix
colliding_pickle2 = collision_blocks2 + appendix

print('-' * 40)
print("Constructed colliding pickle files")

# check if valid pickle files
try:
    pickle.loads(colliding_pickle1)
    pickle.loads(colliding_pickle2)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
else:
    print("Final pickle files are valid!")

print('-' * 40)
# check md5
md5_1 = hashlib.md5(colliding_pickle1).hexdigest()
md5_2 = hashlib.md5(colliding_pickle2).hexdigest()

if md5_1 != md5_2:
    print("MD5s are different")
    print(f"MD5(1): {md5_1}")
    print(f"MD5(2): {md5_2}")
    sys.exit(1)
else:
    print(f"MD5(1): {md5_1}")
    print(f"MD5(2): {md5_2}")
    print("MD5 check successful!")

print('-' * 40)
print("You can check the file values with:\npython -m pickle colliding_pickle1.pkl colliding_pickle2.pkl")

# save the colliding pickle files
with open(args.output1, "wb") as f:
    f.write(colliding_pickle1)
with open(args.output2, "wb") as f:
    f.write(colliding_pickle2)