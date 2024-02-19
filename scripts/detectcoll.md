Detectcoll (unsafe) outputs.

# MD5

Typical output:
```
Found collision in block 1:
   dm: dm2=ffffff00 dm4=80000000 dm11=ffff8000 dm14=80000000
   ihv1=8efacc06affe94f47b23192c60b5f20a
   ihv2=8efacbe6daacdcd47de3190c62b5f1ea
*coll* d320b6433d8ebc1ac65711705721c2e1 single-cpc1.bin
ae6588e7d5ae38f2cb28bdbc427fc2c55597abbe single-cpc1.bin
```


## IPC

- FastColl: dm: `4,11,14` / dihv: `7,76,76,76` (Wang)

- Unicoll1: dm: `2` / dihv: `7,75,765,7`
- Unicoll2: no detection
- Unicoll3: dm: `6,9, 15` / dihv: `765,7650,750,7650`

- Apop: dm: ` ` / dihv: `7,7,7,7`

- Single block IPC: dm: `8, 13` / 'dihv: `,,,`


## CPC
- Flame: dm: `4,11,14` / dihv: `7,63210,765432,765432`

Hashclash CPC: dm: `11` / dihv: `,643,,6`
- pe, jpg/pe, pdf/pe, ca, Zinsider (3mf / docx / epub / xps / xlsx / pptx / oxps), pileup (block 10 & block 20)

- single block CPC: dm: `2,4,11,14` / dihv: `21,7654321,651,621`

# SHA1

Output:

```
Partial collision found
Found collision in block 3 using DV II(52,0):
   dm: dm0=0c000002 dm1=3ffffff0 dm2=abfffff4 dm3=fbfffffc dm4=4c00000a dm5=dffffff0 dm6=e400001c dm7=d4000014 dm8=fbfffffe dm9=bffffff0 dm10=8c000004 dm11=e4000004 dm12=84000008 dm13=affffff0 dm14=00000004 dm15=47fffff0
   ihv1=4ea962697c876e2674d107f0fec6798414f5bf45
   ihv2=4ea962697c876e2674d107f0fec6798414f5bf45
```

Shattered (IPC): dm: `0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15`
- `dm0=0c000002 dm1=3ffffff0 dm2=abfffff4 dm3=fbfffffc dm4=4c00000a dm5=dffffff0 dm6=e400001c dm7=d4000014 dm8=fbfffffe dm9=bffffff0 dm10=8c000004 dm11=e4000004 dm12=84000008 dm13=affffff0 dm14=00000004 dm15=47fffff0` side A, block +0
- `dm0=f3fffffe dm1=bffffff0 dm2=8c00001c dm3=ec000004 dm4=43fffff6 dm5=dffffff0 dm6=1bffffe4 dm7=ec000014 dm8=fc000002 dm9=40000010 dm10=54000004 dm11=e4000004 dm12=83fffff8 dm13=90000010 dm14=00000004 dm15=47fffff0` side A, block +1
- `dm0=f3fffffe dm1=c0000010 dm2=5400000c dm3=04000004 dm4=b3fffff6 dm5=20000010 dm6=1bffffe4 dm7=2bffffec dm8=04000002 dm9=40000010 dm10=73fffffc dm11=1bfffffc dm12=7bfffff8 dm13=50000010 dm14=fffffffc dm15=b8000010` side B, block +0
- `dm0=0c000002 dm1=40000010 dm2=73ffffe4 dm3=13fffffc dm4=bc00000a dm5=20000010 dm6=e400001c dm7=13ffffec dm8=03fffffe dm9=bffffff0 dm10=abfffffc dm11=1bfffffc dm12=7c000008 dm13=6ffffff0 dm14=fffffffc dm15=b8000010` side B, block +1


Shambles (CPC):
- `dm0=f4000002 dm1=3ffffff0 dm2=6c00001c dm3=e4000004 dm4=5bfffffa dm5=1ffffff0 dm6=24000014 dm7=abffffec dm8=f4000002 dm9=c0000010 dm10=93ffffe4 dm11=1bfffffc dm12=43fffff8 dm13=4ffffff0 dm14=fffffffc dm15=a8000010`
- `dm0=0bfffffe dm1=c0000010 dm2=93ffffe4 dm3=1bfffffc dm4=a4000006 dm5=e0000010 dm6=dbffffec dm7=54000014 dm8=0bfffffe dm9=3ffffff0 dm10=6c00001c dm11=e4000004 dm12=bc000008 dm13=b0000010 dm14=00000004 dm15=57fffff0`
