# FOCAL-11 V11-01C for RSX-11M / RSX-11M-PLUS

A fixed build of FOCAL-11, the native RSX-11 port of DEC's interpreted FOCAL language, from the DECUS RSX87A collection (directory 312315, submitted by Glenn Everhart). FOCAL is a BASIC-like language from the late 1960s; Lunar Lander was originally written in it.

This version fixes a crash in the `FEXP` (e^x) function: calling `FEXP(0.0)` recursed forever and crashed the task with `SST abort, Bad stack`. Built and tested on RSX-11M-PLUS V4.6 on a PiDP-11 (SimH). The version string changes from `V11-01B` to `V11-01C`.

## What's fixed

`XFEXP` in `FCLMAI.MAC` computes e^x by repeatedly halving x and squaring the result as the recursion unwinds. It stops recursing when the floating-point exponent drops below -8. Zero is stored with an exponent of 0, which never drops below -8, and squaring 0.0 still gives 0.0. So `FEXP(0.0)` recursed forever until the stack ran off the bottom of memory. Valid programs hit this whenever the argument is exactly zero, for example `FEXP(-T*I)` with `I` starting at 0.

Making the stack bigger doesn't help, because the recursion is infinite, not just deep. Every other recursive routine of this kind already had a recursion-depth guard; `XFEXP` was the only one missing it. I added the same guard that `XFATN2` (arctangent) uses: when the stack gets low, stop recursing and fall through to the direct series, which correctly gives 1.0 at x=0.

```diff
--- FCLMAI.MAC (V11-01B, original)
+++ FCLMAI.MAC (V11-01C, patched)
@@ -979,7 +979,7 @@
-.ASCII "C:RSX FOCAL-11 V11-01B ";VERSION ID
+.ASCII "C:RSX FOCAL-11 V11-01C ";VERSION ID
@@ -5196,6 +5196,8 @@
 	.FPP. FGET+FROM+STACK	;RESTORE ARG TO CELL
 	BR	$14.2
 $14.15:
+	CMP	SP,#100	;RUNNING OUT OF STACK TO RECURSE? (E.G. ARG=0.0 NEVER SHRINKS)
+	BLOS	$14.16	;YES, DON'T CRASH FOCAL--GET OUT.
 	.FPP. FGET+FROM+STACK
 	DEC	BE	;DIVIDE BY 2 BY DECREASING EXPONENT
 	.FPP. FPUT+INTO+STACK	;SAVE ON STACK
@@ -5204,6 +5206,8 @@
 	.FPP. FML$+FROM+STACK	;SQUARE
 	CMP	(SP)+,(SP)+	;RETURN AFTER CLEARONG STACK
 	RTS	PC
+$14.16:	.FPP. FGET+FROM+STACK	;GIVE UP RECURSING, USE DIRECT SERIES INSTEAD
+	BR	$14.2
 $14.2:	.FPP. FPUT+INTO+STACK		;SAVE  OLD VALUE
```

`FCLBLD.TKB` also differs from the original in one line: `STACK=1000` became `STACK=4000`. This was tried while diagnosing the crash. It does not fix the bug (the guard does), but it is harmless and is left in.

## Files

| File | Description |
|---|---|
| `FCLMAI.MAC` | Main interpreter (patched, V11-01C) |
| `FCLINI.MAC` | One-time initialization code (unchanged) |
| `FCLPR.MAC` | Assembly parameters (feature switches and FPP settings), assembled with both sources (unchanged) |
| `FCLBLD.TKB` | Task-builder command file |

Use `FCLBLD.TKB`, not the `FCLBLD.CMD` variant from the DECUS directory. The `.CMD` file is for a VAX/RSX-compatibility build and needs an extra `ASSLUN.OBJ` workaround.

## Building under RSX-11M / RSX-11M-PLUS

1. Copy the four files to the RSX system with **ASCII**-mode FTP. This example uses `DU1:[FOCAL]`; the FTP daemon's default directory is the login UIC, so use `cd DU1:[FOCAL]` in the `ftp` session:

        ftp frodo
        (log in)
        ascii
        cd DU1:[FOCAL]
        mput FCLMAI.MAC FCLINI.MAC FCLPR.MAC FCLBLD.TKB
        quit

2. On RSX, set the default directory:

        SET DEFAULT DU1:[FOCAL]

3. Switch the command line to MCR. The `MAC` command below uses MCR syntax, which DCL's `MACRO` command rejects:

        SET /MCR=TI:

4. Assemble the main source. An informational message `ASSEMBLED USING HARDWARE FPP INSTRUCTIONS--TKB ACCORDINGLY` is expected. It is a `.PRINT` directive in the source, not an error. It reminds you to link with FPP support, which `FCLBLD.TKB` already does with `/FP`. Your machine needs a floating-point processor (the PDP-11/70 in SimH and on the PiDP-11 has one):

        MAC FCLMAI=FCLPR,FCLMAI

5. Assemble the initialization source:

        MAC FCLINI=FCLPR,FCLINI

6. Switch back to DCL:

        SET /DCL=TI:

7. Task-build it:

        TKB @FCLBLD.TKB

   This produces `FCL.TSK` (92 blocks).

8. Run it:

        RUN FCL.TSK

You get the `*` prompt. Press Ctrl-Z to exit.

### Optional: install it as the system command `FCL`

This needs a privileged session, because the sandboxed `USER` account can't write to `LB:[1,1]`:

    PIP LB:[1,1]FCL.TSK/CO=DU1:[FOCAL]FCL.TSK
    INS LB:[1,1]FCL.TSK/TASK=...FCL

After that, typing `FCL` at the DCL prompt starts FOCAL. Add the `INS` line to your `STARTUP.CMD` to install it at every boot.

## Testing the fix

Type this damped sine wave program in at the `*` prompt. It crashes the original build when `I` reaches 0 and `FEXP(0.0)` is called. It runs on V11-01C.

    1.03 ASK "SINE WAVE AMPLITUDE: ", AMPL, !
    1.04 ASK "DAMPING FACTOR COEFFICIENT: ", T, !
    1.05 FOR K=0,60; TYPE "."
    1.06 TYPE !; FOR I=0,.5,15; DO 1.11; TYPE "*"; DO 3
    1.07 QUIT
    1.11 FOR J=0,30+AMPL*FSIN(I)*FEXP(-T*I); DO 2; T " "

    2.10 IF (J-32) 2.3, 2.2, 2.3
    2.20 TYPE "."
    2.30 RETURN

    3.10 IF (31-J) 3.3, 3.2; FOR K=J,30; TYPE " "
    3.20 TYPE "."
    3.30 TYPE !; RETURN

Type `GO` to run it. With amplitude 15 and damping factor .135 you get a damped sine wave:

    *go
    SINE WAVE AMPLITUDE: 15

    DAMPING FACTOR COEFFICIENT: .135

    .............................................................
                                  * .
                                    .     *
                                    .          *
                                    .           *
                                    .         *
                                    .     *
                                    *
                               *    .
                            *       .
                           *        .
                           *        .
                             *      .
                                 *  .
                                    *
                                    .  *
                                    .    *
                                    .    *
                                    .  *
                                    *
                                  * .
                                *   .
                               *    .
                               *    .
                                *   .
                                 *  .
                                  * .
                                    *
                                    *
                                    . *
                                    *
                                    *

## Handy FOCAL commands

Save a program, for example to `HELLO.FCL`:

    * L O HELLO.FCL       (LIBRARY OPEN output file)
    * L W A               (LIBRARY WRITE ALL: writes the whole program)
    * L C O               (LIBRARY CLOSE OUTPUT)

Load a program:

    * @HELLO.FCL

Exit FOCAL with Ctrl-Z.

For the language itself, see the *PDP-8-I FOCAL Programming Manual* (DEC-08-AJAB-D). The command set carries over to FOCAL-11, apart from the PDP-8 hardware features.

## Credits

FOCAL-11 for RSX was written by Glenn Everhart and distributed through DECUS (RSX87A collection, directory 312315), also available at <http://www.ibiblio.org/pub/academic/computer-science/history/pdp-11/rsx/decus/rsx87a/312315/>. The original FOCAL language is by Digital Equipment Corporation. The `FEXP` recursion fix (V11-01C) is by Eric C. Neilson, September 2026; it was first posted to the [PiDP-11 Google group](https://groups.google.com/g/pidp-11/c/XtKQ_YrY03c).
