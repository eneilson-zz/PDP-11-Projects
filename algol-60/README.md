# ALGOL-60 (DECUS 11-231) for RSX-11M / RSX-11M-PLUS

This is a ready-to-install build of the DECUS 11-231 ALGOL-60 compiler and interpreter, written by Gregory D. Hosler of Digital Equipment Corporation (1976-77), running under RSX-11M-PLUS V4.6 on a PiDP-11 (SimH). ALGOL was the standard language for publishing algorithms in the 1960s and the ancestor of Pascal, Simula, Ada and the C-style block structure.

The compiler turns ALGOL source into interpreted P-code. A small interpreter task runs both the compiler (itself a compiled ALGOL program, `ALGOL.ALG`) and your programs.  **There is no floating point.**

## What's different from the DECUS kit

The kit (included unmodified in `kit/`) is documented for RSX-11M and RT-11 but needs three fixes to work well on RSX-11M-PLUS V4.6:

1. **Path patch.** The interpreter and the compiler look up their default compiler and error-message files with the hard-coded 9-character string `[001,002]` and no device. On RSX-11M-PLUS that spec fails with `PARSE ERROR, FCS ERROR = -26`, even though `DU0:[1,2]ALGOL` typed by hand works. The fix is to replace the string with the same-length `DU0:[1,2]` (2 places in the task image). The compiler's own error-message file is named by a single literal, `ALGOL.ERR[001,002]` (name first, UIC last), which FCS cannot parse either, so compile errors showed only the source line and a bare marker with no message text. That literal is rewritten as `DU0:[1,2]ALGOL.ERR` (also 18 characters), and compile errors now print their messages (for example `MISSING ';' OR 'END'.`). `build/patch_algol.py` does it.
2. **Object file conversion.** The interpreter is distributed as RT-11-format `.OBJ` files. `TKB` rejects them if you just FTP them ("illegal format", in both fixed and variable record modes), so they have to be converted with `FLX` from an RT-11 volume. The prebuilt, patched `bin/ALGOL.TSK` here saves you that step.
3. **Prompt artifact.** The compiler prints its banner and `#` prompt as a 10-word record (`WRITE(TTY[0],10,CSI)`). The text is 19 bytes, so the source pads the last word with `3"200"`, a byte with only bit 7 set (0x80). On a 7-bit terminal of the day bit 7 was dropped and the pad was invisible; over an 8-bit telnet connection it arrives as a real 0x80 byte, which a modern terminal draws as a garbage character after every `#`. It is harmless but ugly. The pad byte is now a space, so the prompt reads `# `. Integer literals are stored in the compiled code as the value shifted left two bits, so the fix changes the operand word `00 02` (128) to `80 00` (32). `build/patch_algol.py` finds it by its neighbouring operands and does it.

## Files

| Path | Description |
|---|---|
| `bin/ALGOL.TSK` | Interpreter task image (EIS version, mapped RSX-11M/M-PLUS), path-patched, task name `...ALG` |
| `bin/ALGOL.ALG` | Compiler (a compiled ALGOL program), path-patched |
| `bin/ALGOL.ERR` | Compiler error messages |
| `bin/ALGRTS.ERR` | Run-time error messages |
| `bin/SWAP.ALG` | 64-block swap file for the interpreter's software virtual memory |
| `src/DEMO.SRC` | Base-conversion demo program from the kit |
| `build/ALGBLD.TKB` | Task-builder file for rebuilding the interpreter |
| `build/patch_algol.py` | Applies the path patch to a task image or `ALGOL.ALG`, and the prompt patch to `ALGOL.ALG` |
| `docs/` | The kit's documentation as plain text (`rsx.doc`, `rt.doc`, `complr.doc`, `binder.doc`, `listng.doc`, `patch.doc`) |
| `kit/` | The original DECUS 11-231 files, unmodified (three floppies: `110231a1`, `a2`, `a3`) |

Everything in `bin/` is a raw block file, not text.

## Installing the prebuilt version

1. Create a working directory (adjust the UIC for your system):

        CREATE/DIRECTORY/OWNER_UIC:[200,1] DU1:[ALGOL]

2. Copy the `bin/` files to `DU1:[ALGOL]` with FTP in **BLOCK** mode, so RSX stores them as fixed-length 512-byte-record files. A plain binary transfer stores them as variable-length records, which corrupts them. Send `DEMO.SRC` in ASCII mode.

        ftp <your pdp-11 system>
        (log in)
        binary
        quote BLOCK
        cd DU1:[ALGOL]
        put bin/ALGOL.TSK ALGOL.TSK
        put bin/ALGOL.ALG ALGOL.ALG
        put bin/ALGOL.ERR ALGOL.ERR
        put bin/ALGRTS.ERR ALGRTS.ERR
        put bin/SWAP.ALG SWAP.ALG
        ascii
        put src/DEMO.SRC DEMO.SRC
        quit

3. In a privileged session, put the compiler and message files where the interpreter looks for them (`[1,2]`), put the task image in `LB:[1,1]`, and install it:

        PIP LB:[1,2]ALGOL.ALG/CO=DU1:[ALGOL]ALGOL.ALG
        PIP LB:[1,2]ALGOL.ERR/CO=DU1:[ALGOL]ALGOL.ERR
        PIP LB:[1,2]ALGRTS.ERR/CO=DU1:[ALGOL]ALGRTS.ERR
        PIP LB:[1,1]ALGOL.TSK/CO=DU1:[ALGOL]ALGOL.TSK
        INSTALL LB:[1,1]ALGOL.TSK/TASK=...ALG

4. To have it installed at every boot, add the same `INSTALL` line to `STARTUP.CMD` next to your other language installs (back the file up first).

## Using it

`ALG` starts the interpreter. There are two different prompts:

| Prompt | What it expects |
|---|---|
| `ALG>` | The name of a compiled program to run, or an empty Enter to load the compiler |
| `#` | A compile command, `output[,listing]=input[/switches]` |

Compile and run the demo (called "demo"):

    $ SET DEFAULT DU1:[ALGOL]
    $ TYPE DEMO.SRC                 (list the source)
    $ ALG
    ALG>                            (press Enter: loads the compiler)
    ALGOL  V06.6.019
    #DEMO=DEMO                      (compile DEMO.SRC to DEMO.ALG)
    ALG>DEMO                        (run it)
                 BASE CHANGE DEMO PROGRAM
         CONVERTS NUMBERS FROM ONE BASE TO ANOTHER
    BASES MUST BE BETWEEN 2 AND 16 (INCLUSIVE)
    ENTER #, INPUT BASE, OUTPUT BASE -- 255,10,16
    255 IN BASE 10 IS FF IN BASE 16
    ENTER #, INPUT BASE, OUTPUT BASE -- ^Z
    ALG>^Z

| What you want | At the `#` prompt |
|---|---|
| Compile | `DEMO=DEMO` (source defaults to `.SRC`, output to `.ALG`) |
| Compile and write a listing file | `DEMO,DEMO=DEMO/L` (writes `DEMO.ALG` and `DEMO.LST`) |
| Compile and run in one step | `DEMO=DEMO/G` |

Notes:

- **Switches are case sensitive.** Use `/L` and `/G` in upper case; `/l` fails.
- **Exiting:** Ctrl-Z ends the running program, then the compiler, then the interpreter.
- **Swap file:** every directory you run from needs its own copy of `SWAP.ALG`. Without it you get `SWAP.ALG --- OPEN ERROR`. Only one session at a time can use a given `SWAP.ALG`; a second session that tried to use it failed to open it (FCS error -29).
- **Versions:** each compile creates a new version of the output files; use `PURGE` to clean them up.
- **Listings and errors:** `docs/listng.doc` explains the debugging columns in a listing and how to read a run-time stack history. `docs/complr.doc` documents the later additions to the language (`CHAIN`, `/G`, multiple input files, indirect command files).
- **Limitations:** no floating point; 16-bit integers only; `FOR` and `THRU` statements may not appear in a block after a compound block (see `docs/complr.doc`, section K). The kit's separate-compilation binder (`BINDER.ALG`, see `docs/binder.doc`) is included in `kit/` but is not installed here.

## Credits and licence

ALGOL-60 for the PDP-11 was written by Gregory D. Hosler of Digital Equipment Corporation and distributed through DECUS as program 11-231. The kit files in `kit/` come from the PDP-11 DECUS archive on ibiblio and were put on floppy by Eric Morton of Prelco Corp. They are included unmodified in `kit/`; the copies in `bin/` differ from them only by the patches described above (the path string in two places in the task image, the error-file name and one prompt byte in the compiler). Sources for the interpreter were never released. The DECUS catalogue describes the program as a user-contributed program with no warranty. The RSX-11M-PLUS port, the patch, and the build and install instructions are by Eric C. Neilson, October 2026.
