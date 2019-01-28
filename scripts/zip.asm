; a nasm source to defines a dual ZIP for MD5 collisions

; build with `nasm -o zip.zip zip.asm`

; Ange Albertini 2018


BITS 32
%include "zip.inc"

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; Replace File 1 and 2 values.

; reminder: incbin "<file>", <start>, <size>

; File 1

%macro file1.name 0
  db 'hello.txt'
%endmacro

%macro file1.content 0
%%start:
  db 'Hello World!', 0ah
file1.compsize equ $ - %%start
%endmacro

file1.compression equ COMP_STORED
file1.decsize     equ file1.compsize
file1.CRC32       equ 0x7d14dddd



; File 2

%macro file2.name 0
    db 'bye.txt'
%endmacro

%macro file2.content 0
%%start:
  db 'Bye World!', 0ah
file2.compsize equ $ - %%start
%endmacro

file2.compression equ COMP_STORED
file2.decsize     equ file2.compsize
file2.CRC32       equ 0xcedb178e


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

                                                            file2:
                                                            istruc filerecord
                                                              at filerecord.frSignature,        db "PK", 3, 4
                                                              at filerecord.frVersion,          dw 0ah
                                                              at filerecord.frCompression,      dw file2.compression
                                                              at filerecord.frCrc,              dd file2.CRC32
                                                              at filerecord.frCompressedSize,   dd file2.compsize
                                                              at filerecord.frUncompressedSize, dd file2.decsize
                                                              at filerecord.frFileNameLength,   dw lfhname2.len
                                                              at filerecord.frExtraFieldLength, dw extra2.len
                                                            iend

                                                            lfhname2:
                                                              file2.name
                                                            lfhname2.len equ $ - lfhname2

                                                            extra2:
                                                              field2:
                                                                .id dw 0
                                                                .len dw extra2.len - 4

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

file1:
istruc filerecord
  at filerecord.frSignature,        db "PK", 3, 4
  at filerecord.frVersion,          dw 0ah
  at filerecord.frCompression,      dw file1.compression
  at filerecord.frCrc,              dd file1.CRC32
  at filerecord.frCompressedSize,   dd file1.compsize
  at filerecord.frUncompressedSize, dd file1.decsize
  at filerecord.frFileNameLength,   dw lfhname1.len
  at filerecord.frExtraFieldLength, dw extra1.len
iend

lfhname1:
  file1.name
lfhname1.len equ $ - lfhname1

extra1:
  field1:
    .id dw 0
    .len dw extra1.len - 4
                                                              extra2.len equ $ - extra2

                                                            data2:
                                                              file2.content
                                                            data2.len equ $ - data2

                                                          ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

                                                          CD2:
                                                            istruc direntry
                                                              at direntry.deSignature,        db "PK", 1, 2
                                                              at direntry.deVersionToExtract, dw 0ah
                                                              at direntry.deCrc,              dd file2.CRC32
                                                              at direntry.deCompressedSize,   dd data2.len
                                                              at direntry.deUncompressedSize, dd data2.len
                                                              at direntry.deFileNameLength,   dw cdname2.len
                                                              at direntry.deFileCommentLength,dw cdcom2.len
                                                              at direntry.deHeaderOffset,     dd file2
                                                            iend

                                                            cdname2:
                                                              file2.name
                                                            .len equ $ - cdname2

                                                            cdcom2:
  extra1.len equ $ - extra1

data1:
  file1.content
data1.len equ $ - data1

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

CD1:
  istruc direntry
    at direntry.deSignature,        db "PK", 1, 2
    at direntry.deVersionToExtract, dw 0ah
    at direntry.deCrc,              dd file1.CRC32
    at direntry.deCompressedSize,   dd data1.len
    at direntry.deUncompressedSize, dd data1.len
    at direntry.deFileNameLength,   dw cdname1.len
    at direntry.deFileCommentLength,dw cdcom1.len
    at direntry.deHeaderOffset,     dd file1
  iend
  cdname1:
    file1.name
  cdname1.len equ $ - cdname1

  cdcom1:

  align 40h, db 0 ; to align EoCD1 for first collision

  cdcom1.len equ $ - cdcom1

CD1.len equ $ - CD1

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

EoCD1:
istruc endlocator
  at endlocator.elSignature,          db "PK", 5, 0x06
  at endlocator.elEntriesInDirectory, db 1
  at endlocator.elDirectorySize,      dd CD1.len
  at endlocator.elDirectoryOffset,    dd CD1
  at endlocator.elCommentLength,      dw EoCD1com.len
iend

EoCD1com:
  db 0, 'M' ; to align prefix to 4 for UniColl collision blocks

  times 104 times 40h db 0 ; end of collision blocks
                                                            align 40h, db 0 ; to align EoCD 2 for 2nd collision

                                                            cdcom2.len equ $ - cdcom2

                                                          CD2.len equ $ - CD2

                                                          ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

                                                            EoCD2:
                                                            istruc endlocator
                                                              at endlocator.elSignature,          db "PK", 5, 0x86 ; 0x06/0x86
                                                              at endlocator.elEntriesInDirectory, db 1
                                                              at endlocator.elDirectorySize,      dd CD2.len
                                                              at endlocator.elDirectoryOffset,    dd CD2
                                                              at endlocator.elCommentLength,      dw EoCD2com.len
                                                            iend

                                                            EoCD2com:
                                                              db 0, 'M' ; to align prefix to 4 for UniColl collision blocks

                                                              times 104 times 40h db 0 ; end of collision blocks

                                                            EoCD2com.len equ $ - EoCD2com
EoCD1com.len equ $ - EoCD1com
