#!/usr/bin/env python3
"""Patch DECUS 11-231 ALGOL for RSX-11M-PLUS.

Two in-place, same-length binary patches:

1. Default file paths (task image AND compiler file).
   The interpreter and the compiler look up their default compiler and
   error-message files with the 9-character string "[001,002]" (no
   device). On RSX-11M-PLUS that spec fails to parse (FCS error -26).
   "DU0:[1,2]" is also exactly 9 characters, so it is patched in place.
   Change DEVICE below if LB: is not DU0: on your system (keep the string
   exactly 9 characters).

2. Stray 0x80 after the compiler's "#" prompt (compiler file only).
   The compiler prints its banner and prompt with WRITE(TTY[0],10,CSI),
   a 10-word record. "ALGOL  V06.6.019", LF, CR, "#" is 19 bytes, so the
   source pads the last word with 3"200" (octal 200 = 0x80). A 7-bit
   terminal ignores bit 7, but an 8-bit connection prints it as a
   garbage character. The pad byte is replaced with a space. Integer
   literals are stored in the P-code as (value << 2), so the operand
   word 0x0200 (128) becomes 0x0080 (32 = space). The statement is found
   by its neighbouring operands: LF (5d05 2800) ... CR (5d05 3400) ...
   128 (5d05 0002).

Usage:  patch_algol.py FILE [FILE ...]   (patches each file in place)
Run it on the task image built from ALGRS1/2.OBJ (path patch only; it
contains no prompt code) and on the compiler code file ALGOL.ALG (both).
"""
import sys

OLD = b"[001,002]"
NEW = b"DU0:[1,2]"
assert len(OLD) == len(NEW) == 9

LF = bytes.fromhex("5d052800")    # literal 10
CR = bytes.fromhex("5d053400")    # literal 13
PAD = bytes.fromhex("5d050002")   # literal 128 (0x80 << 2)
SPACE = (0x20 << 2).to_bytes(2, "little")


def patch_prompt(data):
    """Return number of prompt pad bytes patched (0 or 1)."""
    hits = []
    i = data.find(PAD)
    while i >= 0:
        win = data[max(0, i - 80):i]
        if LF in win and CR in win:
            hits.append(i)
        i = data.find(PAD, i + 1)
    if len(hits) != 1:
        return 0
    i = hits[0]
    data[i + 2:i + 4] = SPACE
    return 1


for path in sys.argv[1:]:
    data = bytearray(open(path, "rb").read())
    n = data.count(OLD)
    data = bytearray(bytes(data).replace(OLD, NEW))
    p = patch_prompt(data)
    open(path, "wb").write(data)
    print(f"{path}: {n} path string(s), {p} prompt pad byte(s) patched")
