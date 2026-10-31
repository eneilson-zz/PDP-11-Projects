#!/usr/bin/env python3
"""Adapt Paul Koning's RSTS/E ALGOL 6.7 compiler source (algol.alg) so the
DECUS 6.6 interpreter on RSX-11 can run it.

6.7 changed every I/O count from words to BYTES (changelog 6.7.001) and the
file record sizes with it. The RSX interpreter is the 6.6 one, which counts
WORDS. This script halves the counts and record sizes, and makes the other
RSX-specific changes, in the source text. Every substitution is asserted to
match exactly the expected number of times, so nothing is silently missed.

Usage: adapt67.py ../algol-rsts/algol.alg ALGOL67.SRC [--errfile=SPEC]

--errfile sets where the compiler looks for its ALGOL.ERR message file. The
default, DU0:[1,2]ALGOL.ERR, suits RSX-11M-PLUS. On RSTS/E (RSX run-time
system) use --errfile=SY:[1,2]ALGOL.ERR.
"""
import sys

args = [a for a in sys.argv[1:] if not a.startswith('--')]
opts = dict(a[2:].split('=', 1) for a in sys.argv[1:] if a.startswith('--') and '=' in a)
src, dst = args[0], args[1]
errfile = opts.get('errfile', 'DU0:[1,2]ALGOL.ERR')
d = open(src, 'rb').read()
# clean-up needed by the 6.6 compiler: 98 form feeds (page breaks at line
# starts, one in front of the outer BEGIN), 433 NUL pad bytes after the
# final END., and the '@T' title card (first line)
d = d.replace(b'\x00', b'').replace(b'\x0c', b'')
lines = d.split(b'\r\n')
if lines and lines[-1] == b'':
    lines = lines[:-1]
assert lines[0].startswith(b'@T')
lines = lines[1:]
t = '\n'.join(x.decode('latin1') for x in lines) + '\n'

def sub(old, new, count=1):
    global t
    n = t.count(old)
    assert n == count, 'expected %d of %r, found %d' % (count, old, n)
    t = t.replace(old, new)

# --- file declarations (record sizes: bytes -> words) ---
sub('CARDIN(KIND=DISK,MAXRECSIZE=80)', 'CARDIN(KIND=DISK,MAXRECSIZE=40)')
sub('CODERECSIZE = 512#,\t\t\t% CODE RECSIZE IN BYTES',
    'CODERECSIZE = 256#,\t\t\t% CODE RECSIZE IN WORDS (RSX/6.6 RUNTIME)')
sub('CREF(KIND=BINARY,MAXRECSIZE=32,TITLE="CREF.DAT")',
    'CREF(KIND=BINARY,MAXRECSIZE=16,TITLE="CREF.DAT")')
sub('INCLUDE(KIND=DISK,MAXRECSIZE=80)', 'INCLUDE(KIND=DISK,MAXRECSIZE=40)')
sub('ERRORF(KIND=BINARY,MAXRECSIZE=64,TITLE="SY:[1,211]ALGOL.ERR")',
    'ERRORF(KIND=BINARY,MAXRECSIZE=36,TITLE="%s")' % errfile)
sub('TTY(KIND=TTY,MAXRECSIZE=80)', 'TTY(KIND=TTY,MAXRECSIZE=40)')

# --- listing output (all WRITEALINE callers pass byte counts) ---
sub('IF NOT LNCT=100 THEN WRITE(LINE,X,LINEOUT);',
    'IF X GTR 0 THEN REPLACE POINTER(LINEOUT)+X BY " " FOR 1;   % PAD BYTE OF AN ODD LINE\n\t  IF NOT LNCT=100 THEN WRITE(LINE,(X+1) DIV 2,LINEOUT);')
sub('WRITE(LINE[0],2,LINEOUT)', 'WRITE(LINE[0],1,LINEOUT)')
sub('WRITE(LINE,80,LINEOUT)', 'WRITE(LINE,40,LINEOUT)')
sub('WRITE(LINE,132,LINEOUT)', 'WRITE(LINE,66,LINEOUT)')
sub('WRITE(LINE,64,TITLE2)', 'WRITE(LINE,32,TITLE2)')
sub('WRITE(CREF,32,X)', 'WRITE(CREF,16,X)')
sub('IF EIGHTYCOL THEN LINE.MAXRECSIZE:=80\n\t  ELSE LINE.MAXRECSIZE:=132;',
    'IF EIGHTYCOL THEN LINE.MAXRECSIZE:=40\n\t  ELSE LINE.MAXRECSIZE:=66;')

# --- source and error-message input ---
sub('READ(INCLUDE,72,CARD)', 'READ(INCLUDE,36,CARD)')
sub('READ(CARDIN,72,CARD)', 'READ(CARDIN,36,CARD)')
sub('READ(ERRORF[X-1],64,AB)', 'READ(ERRORF[X-1],26,AB)')   # 6.6 reads 26 words

# --- code file output ---
sub('WRITE(CODE[DA],512,SIGH)', 'WRITE(CODE[DA],256,SIGH)')
sub('WRITE(CODE[0],14,PRTA[*])', 'WRITE(CODE[0],7,PRTA[*])')
sub('WRITE(CODE[0],22,PRTA[*])', 'WRITE(CODE[0],11,PRTA[*])')
sub('WRITE(CODE[J:=DA],T*2,PRTA[*])', 'WRITE(CODE[J:=DA],T,PRTA[*])')

# --- console I/O ---
sub('WRITE(TTY[1],32,CSI)', 'WRITE(TTY[1],16,CSI)')
sub('WRITE(TTY[0],2,CSI)', 'WRITE(TTY[0],1,CSI)')
sub('READ(TTY,78,CSI)', 'READ(TTY,39,CSI)')
sub('REPLACE STR BY "?Illegal switch";\n\t  WRITE(TTY,15,STR);',
    'REPLACE STR BY "?Illegal switch ";\n\t  WRITE(TTY,8,STR);')
sub('REPLACE STR BY "?Input file not found";\n\t\tWRITE(TTY,21,STR);',
    'REPLACE STR BY "?Input file not found ";\n\t\tWRITE(TTY,11,STR);')
sub('REPLACE STR BY "?No input file";\n\t  WRITE(TTY,14,STR);',
    'REPLACE STR BY "?No input file";\n\t  WRITE(TTY,7,STR);')
sub('WRITE(TTY,19,LINEOUT)', 'WRITE(TTY,10,LINEOUT)')

# --- date/time: the 6.6 interpreter implements TIME(1)..TIME(5) only (6.7 adds
# TIME(0), seconds) and only with constant arguments (no TIME(J)). Read 1..5
# unrolled, zero the seconds slot, check the minute twice.
sub('GETTIME: FOR J:=0 STEP 1 UNTIL 5\n\tDO CTIME[J]:=TIME(J);\n\tIF TIME(0) NEQ CTIME[0] THEN GO GETTIME;',
    'GETTIME: CTIME[0]:=0;\n\tCTIME[1]:=TIME(1); CTIME[2]:=TIME(2); CTIME[3]:=TIME(3);\n\tCTIME[4]:=TIME(4); CTIME[5]:=TIME(5);\n\tIF TIME(1) NEQ CTIME[1] THEN GO GETTIME;')

# end-of-compile statistics also use TIME(0) (seconds), which the 6.6 interpreter
# lacks, and divide by an elapsed time that is 0 for compiles under a second.
# Treat seconds as 0 and keep the divisor non-zero.
# (LINECOUNT*60 overflows 16 bits for sources over 546 lines when the compile
# takes under 10 minutes, which only a fast machine reaches: divide first.)
sub('THEN J:=(LINECOUNT*60)/(J*60+TIME(0)-CTIME[0])', 'THEN J:=(LINECOUNT DIV (J*60+1))*60')
sub('CTIME[0]:=TIME(0)-CTIME[0];', 'CTIME[0]:=0;')

# --- code file header words the RSX (6.6) interpreter expects, and the 6.6
# default file extensions (source .SRC, code .ALG; 6.7 uses .ALG and .ALC).
sub('PRTA[3]:=REAL(LEVEL=1);', 'PRTA[3]:=REAL(LEVEL=0);')       # 6.6: INHIBIT SEPARATELY
sub('PRTA[9]:=REVNO;', 'PRTA[9]:=3"33066";')                     # "66": RSX interpreter revision
sub('      REPLACE Q BY ".ALG",0 FOR 1;\n\t      REPLACE CARDIN.TITLE BY STR;',
    '      REPLACE Q BY ".SRC",0 FOR 1;\n\t      REPLACE CARDIN.TITLE BY STR;')
sub('THEN REPLACE Q BY ".ALC",0 FOR 1;', 'THEN REPLACE Q BY ".ALG",0 FOR 1;')

# --- listing page header date: 6.7 expects RSTS conventions (month 0-11, year
# as an offset from 1900); the RSX interpreter gives month 1-12 and the year
# (4-digit here; handle 2-digit too).
sub('"Jul","Aug","Sep","Oct","Nov","Dec"),"-19",\n\t\t  YR FOR 2 DIGITS;',
    '"Jul","Aug","Sep","Oct","Nov","Dec"),"-",\n\t\t  ZS(YR+1900*REAL(YR LSS 100)+100*REAL(YR LSS 70),4);')
sub('ZS(DA,2),"-",CASE MO OF (', 'ZS(DA,2),"-",CASE MO-1 OF (')

# --- default record sizes the compiler emits for user FILE declarations ---
sub('IF EIGHTYCOL\t% IS 80 FOR 80 COL PRINTER\n\t\t\t\tTHEN 80\n\t\t\t\tELSE 132;',
    'IF EIGHTYCOL\t% IS 40 WORDS FOR 80 COL PRINTER\n\t\t\t\tTHEN 40\n\t\t\t\tELSE 66;')
sub('THEN MAX:=512;\t% DEFAULT RECORD SIZE FOR BIN FILES',
    'THEN MAX:=256;\t% DEFAULT RECORD SIZE (WORDS) FOR BIN FILES')

open(dst, 'wb').write(t.replace('\n', '\r\n').encode('latin1'))
print('wrote', dst, len(t.split('\n')) - 1, 'lines')
