# FIG-FORTH v1.4 for PDP-11 (RSX-11M)

A patched build of John S. James's PDP-11 FIG-FORTH (September 1979, Forth Interest Group), based on the v1.3 version distributed in the DECUS archive and at <http://www.stackosaurus.com/figforth.html>. 

Built and tested as a hosted task under RSX-11M-PLUS on a PiDP-11 (SimH). It assembles with `RSX11=1` set in `forth.mac`; see Chapter IX of `figforth.doc` for the bring-up options.

## What's fixed relative to the original v1.3

### 1. `?` after word names on modern terminals

FIG-FORTH sets the high bit on the last character of every dictionary name as an end-of-name marker, assuming a 7-bit terminal would not display it. Modern terminal emulators treat that byte as invalid and print `?`. Because of how the output is packed, it only shows up on every other word.

Before (`VLIST`):

    NF?   CF?   LF?   LATEST   TRAVERSE   -DUP   SPAC?   RO?   ?   ?

After:

    NFA   CFA   LFA   LATEST   TRAVERSE   -DUP   SPACE   ROT   >   <

The fix is in the `ID.` word of `forth.mac`. It masks the high bit on the last character of its scratch copy of the name in `PAD` just before `TYPE`. The real dictionary entries are never modified, so `FIND` and everything else that relies on the marker bit still work.

```diff
--- FORTH.MAC (v1.3, original)
+++ FORTH.MAC (v1.4, patched)
@@ -1406,7 +1406,14 @@
      HEAD    203,ID.,256,IDDOT,DOCOL                 ; ***** ID.
      .WORD   PAD,LIT,40,LIT,137,FILL,DUP
      .WORD   PFA,LFA,OVER,SUB,PAD,SWAP,CMOVE
-     .WORD   PAD,COUNT,LIT,37,AND,TYPE,SPACE,SEMIS
+     .WORD   PAD,COUNT,LIT,37,AND
+;  MASK OFF THE HIGH BIT (END-OF-NAME MARKER) ON THE LAST CHARACTER OF
+;  THE LOCAL PAD COPY ONLY, SO IT DISPLAYS CORRECTLY ON A 7-BIT TERMINAL.
+;  THE REAL DICTIONARY ENTRY IS NEVER TOUCHED (FIND STILL NEEDS ITS
+;  MARKER BIT INTACT), ONLY THIS SCRATCH COPY IN PAD.
+     .WORD   DUP,TOR,OVER,PLUS,LIT,1,SUB
+     .WORD   DUP,CAT,LIT,177,AND,SWAP,CSTOR
+     .WORD   FROMR,TYPE,SPACE,SEMIS
 ;
@@ -1482,7 +1489,7 @@
-     .ASCII  /FIG-FORTH  V 1.3 /
+     .ASCII  /FIG-FORTH  V 1.4 /
```

### 2. Stray `?` every 512 bytes in `FORTH.DAT`

This one deviates from the v1.3 sources: the `FORTH.DAT` as distributed on the DECUS-archive `FIGFORTH.DSK` RL02 image had its record format set to VARIABLE, which embedded a 2-byte length header every 512 bytes. `FORTH.MAC` does not account for VARIABLE record formats, so a `?` appeared every 512 bytes in the screens. The `FORTH.DAT` in this repo is the full 8192-screen set as a raw block image, with no record headers. See step 3 below for how to copy it to RSX correctly.

Before and after the `forth.mac` patch, the `1 LOAD` messages look like this:

    LOADING EDITOR... ? ISN'T UNIQUE ? ISN'T UNIQUE        (before)
    LOADING EDITOR... R ISN'T UNIQUE I ISN'T UNIQUE        (after)

## Files

| File | Description |
|---|---|
| `forth.mac` | MACRO-11 source, patched (v1.4) |
| `FORTH.DAT` | Screens file (editor, assembler, string package, ...), record-format corruption fixed |
| `figforth.doc` | User's guide, with a changelog header noting the v1.4 changes |

## Building under RSX-11M / RSX-11M-PLUS

These steps were used to build and run v1.4 on RSX-11M-PLUS on a PiDP-11 (SimH). The distributed `forth.mac` is already configured for RSX-11M (`RSX11=1`, `EIS=1`; `RT11`, `ALONE` and `LINKS` commented out).

1. On the RSX system, create a directory for the project (adjust the UIC for your system):

        CREATE/DIRECTORY/OWNER_UIC:[200,1] DU1:[FIGFORTH]
        SET DEFAULT DU1:[FIGFORTH]

2. Copy `forth.mac` from this repo to `DU1:[FIGFORTH]FORTH.MAC` using **ASCII**-mode FTP (`ascii`, `cd DU1:[FIGFORTH]`, `put forth.mac FORTH.MAC`). It is source text, so ASCII is safe.

3. Copy `FORTH.DAT` from this repo to `DU1:[FIGFORTH]FORTH.DAT` with FTP. It is a raw 8,388,608-byte block image (16384 blocks), so it must be sent in **BLOCK** mode so that RSX stores it as a fixed-length, 512-byte-record file. A plain binary transfer stores it as variable-length records, which puts 2-byte record-length headers in the data and brings back the stray `?` characters. From the directory containing `FORTH.DAT`:

        ftp frodo
        (log in)
        binary
        quote BLOCK
        cd DU1:[FIGFORTH]
        put FORTH.DAT
        quit

    `quote BLOCK` is the key command. The server answers `200 BLOCK structured files enabled.` Send it after `binary` and before `put`. The transfer of the whole file takes about half a minute.


4. Assemble the source. The DCL command is `MACRO`, not `MAC`:

        MACRO/LIST FORTH

5. Check the listing for assembly errors. The summary line must say `Errors detected: 0`:

        SEARCH FORTH.LST "Errors detected"

6. Task-build it. Don't skip this step: a stale `FORTH.TSK` looks exactly like a real bug.

        TKB FORTH,FORTH=FORTH

7. Run it. The banner should read `FIG-FORTH  V 1.4`:

        RUN FORTH

8. At the FORTH prompt, load the editor, assembler and string packages. You should see only `ISN'T UNIQUE` warnings, with clean word names and no stray `?`:

        1 LOAD

9. Type `BYE` to exit back to DCL.

If a fresh `RUN FORTH` fails with `DISK READ ERROR # 1`, the `FORTH.DAT` file may still carry a leftover lock from a task that was killed. Clear it with:

    PIP DU1:[FIGFORTH]FORTH.DAT/UN

## Credits

Original PDP-11 FIG-FORTH by John S. James and the Forth Interest Group. The standalone and RSX distribution is maintained at stackosaurus.com. v1.4 fixes by Eric C. Neilson, September 2026.
