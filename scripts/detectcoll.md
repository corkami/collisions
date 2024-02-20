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

- FastColl: dm: `4,11,14` / dihv: `31,31,25,31,26,25,31,25` (Wang)

- Unicoll1: dm: `2` / dihv: `31,31,23,31,27,26,25,24,23,31`
- Unicoll2: no detection
- Unicoll3: dm: `6,9, 15` / dihv: `31,24,23,31,24,23,3,2,1,31,23,1,31,24,23,1`

- Apop: dm: ` ` / dihv: `31,31,31,31`

- Single block IPC: dm: `8, 13` / 'dihv: ` `


## CPC
- Flame: dm: `4,11,14` / dihv: `31,26,25,15,14,13,12,11,10,9,5,4,3,0,31,26,25,18,17,16,15,14,9,31,25,12,11,10,9`

Hashclash CPC: dm: `11` / dihv: `30,10,9,0,9,9`
- pe, jpg/pe, pdf/pe, ca, Zinsider (3mf / docx / epub / xps / xlsx / pptx / oxps), pileup (block 10 & block 20)

- single block CPC: dm: `2,4,11,14` / dihv: `10,9,8,7,6,5,30,29,28,26,24,22,20,17,14,11,5,26,25,23,22,5,25,9,8,7,6,5`

# SHA1

Output:

```
Partial collision found
Found collision in block 3 using DV II(52,0):
   dm: dm0=0c000002 dm1=3ffffff0 dm2=abfffff4 dm3=fbfffffc dm4=4c00000a dm5=dffffff0 dm6=e400001c dm7=d4000014 dm8=fbfffffe dm9=bffffff0 dm10=8c000004 dm11=e4000004 dm12=84000008 dm13=affffff0 dm14=00000004 dm15=47fffff0
   ihv1=4ea962697c876e2674d107f0fec6798414f5bf45
   ihv2=4ea962697c876e2674d107f0fec6798414f5bf45
```

Shattered (IPC): dm: `0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15`, dihv: ` `, `12,11,10,9,5,4,2,1,8,7,5,4,1,31`
Shambles (CPC): dm: `0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15`, dihv: `12,11,10,9,5,4,2,1,8,7,5,4,1,31`
