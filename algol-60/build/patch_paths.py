#!/usr/bin/env python3
"""Patch the built-in file paths of DECUS 11-231 ALGOL for RSX-11M-PLUS.

The interpreter and the compiler look up their default compiler and
error-message files with the 9-character string "[001,002]" (no device).
On RSX-11M-PLUS that spec fails to parse (FCS error -26). The replacement
"DU0:[1,2]" is also exactly 9 characters, so it can be patched in place.

Usage:  patch_paths.py FILE [FILE ...]   (patches each file in place)
Apply it to the task image built from ALGRS1/2.OBJ (2 occurrences) and to
the compiler code file ALGOL.ALG (1 occurrence). Change DEVICE below if
LB: is not DU0: on your system (keep the string exactly 9 characters).
"""
import sys

OLD = b"[001,002]"
NEW = b"DU0:[1,2]"
assert len(OLD) == len(NEW) == 9

for path in sys.argv[1:]:
    data = bytearray(open(path, "rb").read())
    n = data.count(OLD)
    if n == 0:
        print(f"{path}: no '[001,002]' found (already patched?)")
        continue
    data = data.replace(OLD, NEW)
    open(path, "wb").write(data)
    print(f"{path}: patched {n} occurrence(s)")
