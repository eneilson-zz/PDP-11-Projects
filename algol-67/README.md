# ALGOL-60 6.7 (Koning's RSTS/E version) on RSX-11M / RSX-11M-PLUS

Paul Koning's [RSTS/E port of PDP-11 ALGOL](https://github.com/pkoning2/algol) (compiler V6.7.003, 1980) built and running on RSX-11M-PLUS, on top of the DECUS ALGOL interpreter from [`algol-60`](../algol-60/). It is the original Folsom/Hosler ALGOL-60 with Koning's revisions to the compiler: a new listing format with statistics, a cross-reference option, and various language changes to make it "resemble the rest of the world more". The 6.7 compiler runs as an ordinary ALGOL program, so no new interpreter or runtime is needed.

> **Prerequisite: install [ALGOL-60 (`algol-60`)](../algol-60/) first.** The 6.7 compiler runs on the interpreter that project installs, and it is built by the 6.6 compiler from that project. Follow the [`algol-60` README](../algol-60/README.md) (release [`algol60-v6.6.19.2`](https://github.com/eneilson-zz/PDP-11-Projects/releases/tag/algol60-v6.6.19.2) or later) and get its demo working on your RSX system before you start here. Then follow [INSTALL.md](INSTALL.md), which builds the 6.7 compiler from the source in this project in about 20 minutes. You only need FTP; no other tools are required.

The compiler is **self-hosting on RSX**: built by the DECUS 6.6 compiler from Koning's source, it compiles its own source into a compiler that is identical to itself apart from one byte, the embedded compile-time stamp.

## How it works

Koning's repository has the compiler as ALGOL source (`algol.alg`), plus the RSTS/E *runtime system* as MACRO-11 source. The runtime can't be reassembled without two RSTS kit files that are not in his repo, and the RSX interpreter from DECUS 11-231 already does that job. So instead of porting the runtime:

1. You compile `ALGOL67.SRC` on RSX with the DECUS 6.6 compiler from [`algol-60`](../algol-60/), which gives `ALGOL67.ALG`, a code file.
2. `ALG` runs `ALGOL67.ALG` like any other ALGOL program, and it compiles your programs into code files that the same interpreter runs.

### What the adaptation changes

Koning's 6.7 differs from the 6.6 that the RSX interpreter implements, mainly because 6.7 counts I/O in **bytes** and 6.6 counts in **words**. Every substitution in the script is asserted to match an exact number of times, so nothing is silently skipped.

| Change | Why |
|---|---|
| Remove the 98 form feeds, the 433 trailing NULs and the `@T` title card | The 6.6 compiler's scanner can't read them (a form feed sits in front of the outer `BEGIN`) |
| Halve every I/O count and `MAXRECSIZE` (`READ`, `WRITE`, `FILE` declarations, `CODERECSIZE`), and divide the byte counts passed to the listing writer `WRITEALINE` | 6.7 counts bytes, the interpreter counts words |
| Pad odd-length console messages with a space, and clear the pad byte of odd-length listing lines | Words are written whole, so an odd byte count would print a stray byte |
| Error file name `SY:[1,211]ALGOL.ERR` becomes `DU0:[1,2]ALGOL.ERR` and its record size becomes 36 words | Use the `ALGOL.ERR` installed by `algol-60` (its messages match 6.7's list one-for-one) |
| Read `TIME(1)` to `TIME(5)` as constants only; treat seconds as 0 | The interpreter has no `TIME(0)` and no variable-argument `TIME` |
| Statistics: divide before multiplying when computing cards per minute | `LINECOUNT*60` overflows 16 bits for sources over 546 lines when the compile takes under 10 minutes, which only a fast machine reaches |
| Code file header: `PRTA[3]:=REAL(LEVEL=0)` and revision stamp `"66"` | The RSX interpreter checks them (it rejects the file with `CODE FILE ERROR` otherwise) |
| Default file extensions: source `.SRC`, code `.ALG` (6.7 uses `.ALG` and `.ALC`) | Same as the 6.6 compiler, so `ALG` finds the output |
| Listing page-header date | 6.7 expects RSTS month and year conventions |

## Files

| Path | Description |
|---|---|
| `bin/ALGOL67.ALG` | A reference copy of the finished compiler (a raw block file, 85,564 bytes), built by the 6.7 compiler itself. You don't install it: you build your own (INSTALL.md), and the second build in step 8 can be compared with this one. |
| `src/ALGOL67.SRC` | Koning's compiler source, already converted for the RSX interpreter (LF line endings), ready to copy to RSX with ASCII FTP and compile |
| `tools/adapt67.py` | The script that made `src/ALGOL67.SRC` from Koning's source. It is a record of exactly what was changed, and is only needed to regenerate the source or make the RSTS variant. |
| `INSTALL.md` | Step-by-step install and build guide, with worked examples and troubleshooting |
| `examples/` | `DEMO.SRC` (the base-conversion demo from the DECUS kit), `HELLO.SRC`, `FACT.SRC`, `PRIMES.SRC`, `RTERR.SRC` (a run-time error), `BAD.SRC` (a syntax error), all compiled with this compiler |
| `rsts/ALGOL.ERR` | A 6.7-format compiler error message file for Koning's RSTS/E runtime (see below) |
| `../algol-rsts/` | Koning's repository, imported unmodified |

## Installing and using it

Install [`algol-60`](../algol-60/) first, then follow [INSTALL.md](INSTALL.md) to build the compiler. Once it is built, compiling and running a program looks like this (the compiler needs a bigger stack than the default, so it is loaded with `/S:4000`):

    $ SET DEFAULT DU1:[ALGOL67]
    $ ALG
    ALG>ALGOL67/S:4000
    RSTS/E Algol Compiler - V6.7.003
    *DEMO=DEMO                      (compile DEMO.SRC to DEMO.ALG)
    0 errors detected.
    ALG>DEMO                        (run it)

INSTALL.md has worked examples (compiling, listings, compile and run-time errors, writing your own program) and a troubleshooting table.

Differences from the 6.6 compiler you will notice:

- The prompt is `*`, and the compiler returns to `ALG>` after **each** compile, so type `ALG>ALGOL67/S:4000` again for the next one.
- Switches (after the input file): `/L` 80-column listing, `/P` print on the terminal, `/E` errors only, `/F` ignore form feeds, `/D` debug, `/C` cross-reference (this writes a `CREF.DAT` data file; the program that formats it is not in Koning's repository). `/G` (compile and go) does not exist in 6.7.
- A listing is requested the same way as before, with a second file name: `DEMO,DEMO=DEMO/L` writes `DEMO.ALG` and `DEMO.LST`.
- Switches are case sensitive, as in 6.6.

## Limitations

- Programs run on the **6.6 interpreter**, so they use 6.6 semantics: I/O counts are in words unless the file is opened in character mode (`MYUSE=3"400"`, as in `DEMO.SRC`). A program written for Koning's 6.7 runtime on RSTS, which counts bytes, needs its counts adjusted.
- The elapsed time in the statistics is always 0 seconds, and cards per minute is approximate, because the interpreter has no seconds.
- Compile-error text comes from the `ALGOL.ERR` file of the DECUS kit. Message numbers match 6.7's list, but about one in six messages (21 of 123) has slightly different wording or capitalisation.
- Compiling the compiler itself takes about two minutes and needs `/S:4000`.

## Notes for RSTS/E

These come from trying to get Koning's compiler running under his RSTS/E runtime system, where two things trip people up.

- **`run unsupp$:algol.alc` fails with `?End of file on device`.** The checked-in `algol.alc` is not truncated. It is a complete file that was built with **256-byte** code records: its header puts the program reference table in record 254, which is byte 65,024, inside the 67,072-byte file. The 6.7.003 runtime and source use **512-byte** records (changelog entry 6.7.003), so the runtime looks at byte 130,048, past the end of the file. The binary is older than the source and runtime next to it.
- **`ALGOL.ERR` is not in the repository.** The compiler reads it with `READ(ERRORF[X-1],64,AB)` from a file with 64-byte records, message *n* in record *n−1*, and its source holds the message list as a comment. `rsts/ALGOL.ERR` is generated from that list (123 messages, 8,192 bytes). Message 83 is 66 characters long and is cut to 64. The `ALGOL.ERR` from the DECUS kit uses 72-byte records, so the two files are not interchangeable.
- **Getting a 6.7 code file for the RSTS runtime.** Compiling Koning's source with the DECUS 6.6 compiler (`ALG>[1,2]ALGOL/S:4000`) gives a 168-block file with 512-byte records, and a program reference table of the same size (798 words) and the same segment counts as his own build. The only differences in the header are the revision stamp (`"66"` where his runtime wants `"67"`, the one thing its loader checks, which is why it answers `Compiler version is incompatable`) and a flag word the loader doesn't look at. Changing byte 19 of that file from `0x36` to `0x37` (`"66"` to `"67"`) should therefore make the runtime accept it. This has not been tried on RSTS/E. If it works, run that compiler on `algol.alg` to produce a genuine 6.7.003 `algol.alc`.
- **On RSTS/E with the RSX run-time system**, the DECUS interpreter runs `ALGOL67.ALG` as it is on RSX-11M-PLUS, with no change to the runtime. If the device name `DU0:` doesn't exist there, edit line 752 of `src/ALGOL67.SRC` before you build, changing `DU0:` to `SY:` in the error file name (see INSTALL.md), or regenerate the source with `python3 tools/adapt67.py ../algol-rsts/algol.alg ALGOL67.SRC --errfile=SY:[1,2]ALGOL.ERR`.

## Credits and licence

The PDP-11 ALGOL compiler was written by Barry James Folsom (1973) and extended by Gregory D. Hosler of Digital Equipment Corporation (1974). The RSTS/E port is by Terry Grieb and Paul Koning, and version 6.7 is Paul Koning's. His repository is under the MIT licence, and `algol-rsts/` here is an unmodified copy with his licence file. The interpreter is DECUS 11-231, as in [`algol-60`](../algol-60/), with the same licensing caveat as there. The adaptation, the RSX build and this documentation are by Eric C. Neilson, October 2026, with the help of Claude.
