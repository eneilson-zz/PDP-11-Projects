# PDP-11 Projects

This repo is a collection of software projects for DEC PDP-11 systems — real hardware, SimH, and PiDP-11 emulators — running operating systems such as RT-11 and RSX-11M-PLUS. These are fixes and enhancements to classic PDP-11 software, written mostly in MACRO-11 assembly.

## Projects

#### [FIG-FORTH v1.4](fig-forth/)

A patched build of John S. James's PDP-11 FIG-FORTH (the Forth Interest Group's 1979 implementation, as distributed in the DECUS archive (v1.3) and maintained by stackosaurus.com). The original displays garbled output on any modern terminal emulator, and its `FORTH.DAT` screen file contains stray bytes. This version fixes both issues:

- **`?` in word names.** FIG-FORTH marks the end of each dictionary name by setting the high bit on the last character, assuming a 7-bit terminal would ignore it. Modern terminals render that byte as `?`, so `VLIST` shows `SPAC?`, `RO?` and similar. A three-line patch to `FORTH.MAC` strips the bit from `ID.`'s private copy of the name in `PAD` just before printing. The dictionary itself is untouched, so `FIND` still works.
- **Stray `?` every 512 bytes in `FORTH.DAT`.** The file on the original RL02 image had its RMS record format set to VARIABLE, which embedded a 2-byte length header every 512 bytes. `FORTH.MAC` reads raw blocks and doesn't account for that, so the headers showed up as `?` in the screens. This is a deviation in the DECUS-distributed `FORTH.DAT` from the v1.3 sources; the file here is rewritten as a plain fixed-record file.

The sign-on banner now reads `FIG-FORTH  V 1.4`. Includes the patched `forth.mac`, the corrected `FORTH.DAT`, and the updated user's guide.

#### [FOCAL-11 V11-01C](focal-11/)

A fixed build of FOCAL-11, the native RSX-11M / RSX-11M-PLUS port of DEC's interpreted FOCAL language (from the DECUS RSX87A collection, directory 312315, by Glenn Everhart). FOCAL is a BASIC-like language from the late 1960s; Lunar Lander was originally written in it. The original crashes the task with `SST abort, Bad stack` whenever a program calls `FEXP(0.0)`:

- **`FEXP(0.0)` recursed forever.** `XFEXP` computes e^x by recursively halving x and squaring on the way back, stopping when the exponent falls below -8. Zero has exponent 0, so it never stops, and the recursion runs the stack off the bottom of memory. All of the other respective functions have a recursion-depth guard; `XFEXP` was the only one without it. A small patch to `FCLMAI.MAC` adds the same guard, falling through to the direct series (which gives 1.0 at x=0).

I bumped the version from `V11-01B` to `V11-01C`. Includes the full patched source, the task-builder file, build and install steps, and a damped sine wave program to confirm the fix.
