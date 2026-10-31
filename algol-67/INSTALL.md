# Installing ALGOL-60 6.7 on RSX-11M / RSX-11M-PLUS

This guide builds Paul Koning's 6.7 ALGOL compiler on RSX from its source, using the 6.6 compiler from the ALGOL-60 project located in this GitHub repository: https://github.com/eneilson-zz/PDP-11-Projects/tree/main/algol-60. You need to install and verify ALGOL-60 6.6 works before compiling and installing ALGOL-60 6.7.

Read [README.md](README.md) first if you want to know how it works and what it can't do.

## Before you start: install ALGOL-60 first

**The 6.7 compiler runs on the ALGOL-60 interpreter, and it is built by the ALGOL-60 compiler.** So the [`algol-60`](../algol-60/) project has to be installed and working on your RSX system before you begin. Follow its [README](../algol-60/README.md), and use release [`algol60-v6.6.19.2`](https://github.com/eneilson-zz/PDP-11-Projects/releases/tag/algol60-v6.6.19.2) or later, which makes compile errors show their message text.

When it's installed, you should have:

- the `ALG` command working,
- `ALGOL.ALG`, `ALGOL.ERR` and `ALGRTS.ERR` in `LB:[1,2]`,
- the interpreter task `ALGOL.TSK` installed (as `...ALG`),
- a `SWAP.ALG` file (`../algol-60/bin/SWAP.ALG`), which you copy into each directory you run from.

Check it before going on:

    $ ALG
    ALG>                      (press Enter)
    ALGOL  V06.6.019
    #                         (the 6.6 compiler; press Ctrl-Z twice to leave)

Then compile and run the demo as described in the ALGOL-60 README. If that works, you're ready.

## What you need

| Requirement | Notes |
|---|---|
| An RSX-11M-PLUS system with the `algol-60` project installed and working | See above. |
| FTP access to the RSX system | You copy the source and examples in with plain `ftp`. |
| A privileged session on RSX | Only to create the work directory. Nothing in `LB:[1,2]` or `LB:[1,1]` changes. |

## 1. Create a work directory

In a privileged session (change the owner UIC to the account that you FTP in with):

    CREATE/DIRECTORY/OWNER_UIC:[200,1] DU1:[ALGOL67]

## 2. Copy the swap file (binary, BLOCK mode)

`SWAP.ALG` is a raw block file, so FTP must store it as a fixed-length 512-byte-record file. That is what `quote BLOCK` does. A plain binary transfer stores it as variable-length records and corrupts it.

    ftp <your RSX-11 system>
    (log in)
    binary
    quote BLOCK
    cd DU1:[ALGOL67]
    put ../algol-60/bin/SWAP.ALG SWAP.ALG
    quit

## 3. Copy the source and the examples (text, plain ASCII)

**Use a new FTP session for this.** `BLOCK` mode stays switched on for the rest of a connection, so text sent in the same session as step 2 is stored as raw blocks and reads back as garbage.

    ftp <your RSX-11 system>
    (log in)
    ascii
    cd DU1:[ALGOL67]
    put src/ALGOL67.SRC ALGOL67.SRC
    put examples/DEMO.SRC DEMO.SRC
    put examples/HELLO.SRC HELLO.SRC
    put examples/FACT.SRC FACT.SRC
    put examples/PRIMES.SRC PRIMES.SRC
    put examples/RTERR.SRC RTERR.SRC
    put examples/BAD.SRC BAD.SRC
    quit

`src/ALGOL67.SRC` is Koning's compiler source, already converted so that the DECUS interpreter can run it (see "What the adaptation changes" in [README.md](README.md)). It has plain LF line endings, so ordinary ASCII FTP sends it correctly.

Check that the files arrived:

    DIRECTORY DU1:[ALGOL67]

`ALGOL67.SRC` should be about 415 blocks and `SWAP.ALG` 64 blocks.

## 4. Build the compiler with the 6.6 compiler

The 6.6 compiler needs a bigger stack for a source this size. Load it with `/S:4000` and **no file name**, which loads the default compiler from `LB:[1,2]`:

    $ SET DEFAULT DU1:[ALGOL67]
    $ ALG
    ALG>/S:4000
    ALGOL  V06.6.019
    #ALGOL67=ALGOL67

`ALGOL67=ALGOL67` means: compile `ALGOL67.SRC` and write the code file `ALGOL67.ALG`.

This takes a few minutes and prints nothing until it finishes. When you get the `ALG>` prompt back with no messages, press Ctrl-Z to leave the interpreter and check:

    DIRECTORY ALGOL67.ALG

It should be 168 blocks. If the compile ends with `STACK OVERFLOW`, you left out `/S:4000`.

## 5. Compile and run the demo

    $ ALG
    ALG>ALGOL67/S:4000

You should see:

    RSTS/E Algol Compiler - V6.7.003

    *

At the `*` prompt, type:

    *DEMO=DEMO
    0 errors detected.

    ALG>

Run the compiled program:

    ALG>DEMO

Enter some numbers as `number,input base,output base`:

    ENTER #, INPUT BASE, OUTPUT BASE -- 255,10,16
    255 IN BASE 10 IS FF IN BASE 16
    ENTER #, INPUT BASE, OUTPUT BASE -- 1010,2,10
    1010 IN BASE 2 IS 10 IN BASE 10
    ENTER #, INPUT BASE, OUTPUT BASE -- FF,16,8
    FF IN BASE 16 IS 377 IN BASE 8

Press Ctrl-Z to leave the demo, and Ctrl-Z again to leave the interpreter.

## 6. Try the other examples

The compiler returns to `ALG>` after **every** compile, so load it again each time:

    ALG>ALGOL67/S:4000
    *HELLO=HELLO
    ALG>HELLO

    ALG>ALGOL67/S:4000
    *FACT=FACT
    ALG>FACT

`FACT` prints a factorial table for 1 to 7, ending with `FACTORIAL OF  7 IS  5040`.

## 7. Check that errors are reported

`BAD.SRC` has a missing semicolon. Compile it:

    ALG>ALGOL67/S:4000
    *BAD=BAD

You should get a message, not just a marker:

    0006      I:=2;
              I
    ********MISSING ';' OR 'END'.
    1 error detected.

If you get `BAD FILE SPECS` instead of the message, your `algol-60` install is older than `algol60-v6.6.19.2`. Upgrade it.

## 8. Make the compiler build itself (optional)

This gives the native 6.7 build, and shows that the compiler works. It takes about two minutes:

    ALG>ALGOL67/S:4000
    *ALGOL67B=ALGOL67
    0 errors detected.

`ALGOL67B.ALG` is the compiler built by 6.7 itself. It is the same as `bin/ALGOL67.ALG` in this project apart from one or two bytes of the compile-time stamp embedded in the file, so you can compare yours with the reference copy there. The first build, `ALGOL67.ALG`, made by the 6.6 compiler, is the same size but differs from it in several thousand bytes. That is expected: the two compilers lay out the generated tables differently, and the programs they compile behave the same. Repeat the step once more with `ALGOL67B` to get `ALGOL67C`: the second and third builds should differ only in the stamp, which shows that the compiler has reached a fixed point.

This was checked on a PiDP-11: the build from the shipped source took 111 seconds, and the compiler it produced compiled and ran the demo correctly.

## Using the compiler: worked examples

Everything below was run on a PiDP-11 under RSX-11M-PLUS. The command to start is always the same: run `ALG`, then load the compiler, then type a compile command at the compiler's `*` prompt. There are three prompts and each takes different input:

| Prompt | Whose it is | What you type |
|---|---|---|
| `$` | RSX | DCL commands (`ALG`, `TYPE`, `DIRECTORY`) |
| `ALG>` | the interpreter | the name of a program to run, or a compiler to load |
| `*` | the 6.7 compiler | a compile command, `[output][,listing]=source[/switches]` |

### Example 1: compile and run a program

`examples/PRIMES.SRC` prints the primes below 100:

    $ SET DEFAULT DU1:[ALGOL67]
    $ ALG
    ALG>ALGOL67/S:4000
    RSTS/E Algol Compiler - V6.7.003

    *PRIMES=PRIMES
    0 errors detected.

    ALG>PRIMES
       2   3   5   7  11  13  17  19  23  29
      31  37  41  43  47  53  59  61  67  71
      73  79  83  89  97
    25 PRIMES BELOW 100

    ALG>

`PRIMES=PRIMES` means "compile `PRIMES.SRC` and write the code file `PRIMES.ALG`". Typing `PRIMES` at `ALG>` runs that code file. Once it is compiled you can run it again at any time without recompiling.

### Example 2: write a listing file

Name a second output file to get a listing:

    ALG>ALGOL67/S:4000
    *PRIMES,PRIMES=PRIMES/L
    0 errors detected.

    ALG>^Z
    $ TYPE PRIMES.LST

The listing starts with the compiler version and the date, then every source line:

    RSTS/E ALGOL compiler, version 6.7.003
    Friday October 30, 2026 at 6:53 PM.
    ...
    10 001:0027       FOR N:=2 STEP 1 UNTIL 99 DO
    11 001:0073       BEGIN
    12 001:0075 2       PRIME:=TRUE;

The columns are the source line number, then `segment:address` (octal) in the compiled code, then the `BEGIN`/`END` nesting count (printed on the lines where it changes), then the source. The end of the listing has statistics (number of segments, symbol table size, working set).

### Example 3: a compile error

`BAD.SRC` is missing a semicolon after `I:=1`:

    *BAD=BAD
    0006      I:=2;
              I
    ********MISSING ';' OR 'END'.
    1 error detected.

    ALG>

It shows the line, marks the place with `I`, and prints the message. No code file is written.

### Example 4: a run-time error

`examples/RTERR.SRC` indexes an array of three elements with 5. It compiles cleanly and fails when it runs:

    *RTERR=RTERR
    0 errors detected.

    ALG>RTERR
    INVALID INDEX
        [01]001:0021

    ALG>

The three numbers after the message are the block nesting level (`01`), the code segment (`001`) and the address in that segment (`0021`, octal). To find the statement, compile with a listing (Example 2) and look for segment `001`, address `0021`.

### Example 5: write your own program

Create a text file such as `HI.SRC` (with EDT, or on your own machine and FTP it in plain ASCII), then compile and run it like Example 1. This is the smallest useful program:

    BEGIN
      FILE TT(KIND=REMOTE,MYUSE=3"400");
      ARRAY BUF[0:39];
      REPLACE BUF BY "HELLO";
      WRITE(TT,5,BUF)
    END.

- `FILE TT(KIND=REMOTE,MYUSE=3"400")` opens your terminal. The `MYUSE=3"400"` makes counts in `WRITE` and `READ` mean **characters**, not words.
- `REPLACE BUF BY "HELLO"` builds a string in an array, and `WRITE(TT,5,BUF)` prints 5 characters of it followed by a new line.
- To print numbers, copy the macro `DEFINE ZS(I,J) = I FOR J ZEROSUPPRESSED DIGITS#;` from the examples and write `REPLACE BUF BY ZS(N,4)`, which formats `N` in 4 columns.
- The last statement ends with `END.`, with the full stop.

`examples/HELLO.SRC`, `FACT.SRC` and `PRIMES.SRC` show loops, recursion and output to the terminal, and `DEMO.SRC` shows reading what the user types.

### Quick reference

    $ ALG                         start the interpreter
    ALG>ALGOL67/S:4000            load the 6.7 compiler (needed for every compile)
    *name=name                    compile name.SRC to name.ALG
    *name,name=name/L             also write the listing name.LST
    ALG>name                      run name.ALG
    Ctrl-Z                        leave the program, then the compiler, then ALG

After every compile, the compiler returns you to `ALG>`, so load it again for the next one. To compile a different source file, type its name instead of `name`; a compiled program can be run from `ALG>` as often as you like.

## Running the compiler from other directories (optional)

Copy `ALGOL67.ALG` to `LB:[1,2]` in a privileged session:

    PIP LB:[1,2]ALGOL67.ALG/CO=DU1:[ALGOL67]ALGOL67.ALG

Then, in any directory that has a `SWAP.ALG`:

    ALG>DU0:[1,2]ALGOL67/S:4000

That is the same form (explicit device and UIC) that loads the 6.6 compiler by hand.

## Other systems and regenerating the source (optional)

**RSTS/E with the RSX run-time system**, where the device name `DU0:` doesn't exist: open `ALGOL67.SRC` in a text editor before step 3 and change the one line (line 752)

    ERRORF(KIND=BINARY,MAXRECSIZE=36,TITLE="DU0:[1,2]ALGOL.ERR"),

to `TITLE="SY:[1,2]ALGOL.ERR"`. The rest of the build is the same.

**Regenerating the source.** `src/ALGOL67.SRC` was made from Koning's `algol.alg` (imported unmodified in [`../algol-rsts/`](../algol-rsts/)) by `tools/adapt67.py`. You don't need to run it, but to check the shipped source, or to apply the changes to a different copy of his source, run this on a Mac or Linux machine:

    python3 tools/adapt67.py ../algol-rsts/algol.alg ALGOL67.SRC

The result is identical to `src/ALGOL67.SRC` apart from line endings (the script writes CR-LF, which an ASCII `ftp` from a Mac would turn into CR-CR-LF, so use the shipped LF file for transfers). Every substitution in the script is checked to match the exact number of times expected, so it stops with an error if the input is not the version it was written for. Add `--errfile=SY:[1,2]ALGOL.ERR` to make the RSTS variant.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `STACK OVERFLOW` while compiling | The default stack is too small. Load the compiler with `/S:4000`. |
| `SWAP.ALG --- OPEN ERROR`, `FCS ERROR = -16` | No `SWAP.ALG` in the current directory. Copy one in (step 2). |
| `SWAP.ALG --- OPEN ERROR`, `FCS ERROR = -29` | Another session is using that `SWAP.ALG`. Only one at a time can. Use a separate directory for each. |
| `FILE NAME ERROR`, or `BAD FILE SPECS` | You typed a compile command (`DEMO=DEMO`) at the `ALG>` prompt. Compile commands go at the compiler's own prompt (`*` once the 6.7 compiler is loaded, `#` for the 6.6 compiler). |
| `CODE FILE ERROR` when you load `ALGOL67` | The build didn't finish, so the code file is incomplete. Check that step 4 ended with no messages, and rebuild. |
| Source lines read back as fragments, or `0 errors` with nothing compiled | A text file was uploaded in `BLOCK` mode. Re-upload it in a **new** FTP session with `ascii`. |
| `?Input file not found` | The compiler adds `.SRC` to the name you give it. Check the file's name and extension. |
| Compile error shows `BAD FILE SPECS` instead of a message | Your `algol-60` install is older than `algol60-v6.6.19.2` and can't find its message file. Upgrade it. |
| Compile finishes but your program behaves strangely | Programs run on the 6.6 interpreter, which counts I/O in words unless a file is opened in character mode (`MYUSE=3"400"`). See the README. |
| The compile in step 4 reports errors | The source was changed in transit. Check that you uploaded `ALGOL67.SRC` in ASCII mode in a new FTP session, and that the file is about 415 blocks. |

## Cleaning up

Files made by the examples can be deleted when you've finished: `DEMO.ALG`, `HELLO.ALG`, `FACT.ALG`, `PRIMES.ALG`, `RTERR.ALG`, any `.LST` files, and old versions with `PURGE`.
