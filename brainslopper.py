import sys, os, argparse
from math import isqrt
from PIL import Image


CMD = {
    (255, 0,   0):   '>', (128, 0,   0):   '<',
    (0,   255, 0):   '+', (0,   128, 0):   '-',
    (0,   0,   255): '.', (0,   0,   128): ',',
    (255, 255, 0):   '[', (128, 128, 0):   ']',
}
COL = {v: k for k, v in CMD.items()}
CW_COL, CCW_COL, NOP_COL = (0, 255, 255), (0, 128, 128), (0, 0, 0)

def cw(d):  return (-d[1],  d[0])   # right->down->left->up
def ccw(d): return ( d[1], -d[0])   # right->up->left->down


def load_grid(fn, scale):
    im = Image.open(fn).convert('RGB')
    px = im.load(); W, H = im.size
    if scale > 1:
        W, H = W // scale, H // scale
        o = scale // 2
        cell = lambda x, y: px[x * scale + o, y * scale + o]
    else:
        cell = lambda x, y: px[x, y]
    return cell, W, H

def decode(fn, scale=1):
    """Follow the IP path and return the linear Brainfuck string."""
    cell, W, H = load_grid(fn, scale)
    x, y, dx, dy = 0, 0, 1, 0
    out = []
    steps = 0; cap = W * H * 64 + 1000   # guard against pathological images
    while 0 <= x < W and 0 <= y < H:
        p = cell(x, y)
        if   p == CW_COL:  dx, dy = cw((dx, dy))
        elif p == CCW_COL: dx, dy = ccw((dx, dy))
        elif p in CMD:     out.append(CMD[p])
        # else: nop
        x += dx; y += dy
        steps += 1
        if steps > cap: break
    return ''.join(out)


def run_bf(code, out=None):
    if out is None: out = sys.stdout.buffer
    match = {}; st = []
    for i, c in enumerate(code):
        if c == '[': st.append(i)
        elif c == ']':
            j = st.pop(); match[i] = j; match[j] = i
    tape = {}; p = 0; cp = 0
    while cp < len(code):
        c = code[cp]
        if   c == '>': p += 1
        elif c == '<': p -= 1
        elif c == '+': tape[p] = (tape.get(p, 0) + 1) & 255
        elif c == '-': tape[p] = (tape.get(p, 0) - 1) & 255
        elif c == '.': out.write(bytes([tape.get(p, 0)])); out.flush()
        elif c == ',':
            ch = sys.stdin.buffer.read(1)
            tape[p] = ch[0] if ch else 0
        elif c == '[':
            if tape.get(p, 0) == 0: cp = match[cp]
        elif c == ']':
            if tape.get(p, 0) != 0: cp = match[cp]
        cp += 1


def encode(code, width=None, scale=1):
    prog = [c for c in code if c in COL]           # keep only real commands
    L = len(prog)
    if L == 0:
        raise ValueError("no Brainfuck commands found in source")

    # auto width: roughly square, >=3 so left-going legs have room for a command
    if width is None:
        width = max(3, isqrt(L) + 2)
    W = width
    if W < 3 and L > W:                            # need width>=3 to wrap
        raise ValueError("width must be >= 3 to wrap multi-row programs")

    grid = {}                                      # (x,y) -> RGB
    x, y, dx, dy = 0, 0, 1, 0
    i = 0; Hmax = 0
    while i < L:
        if dx == 1 and x == W - 1:                 # right edge U-turn: two CW
            grid[(x, y)] = CW_COL; grid[(x, y + 1)] = CW_COL
            y += 1; x -= 1; dx, dy = -1, 0
            Hmax = max(Hmax, y); continue
        if dx == -1 and x == 0:                     # left edge U-turn: two CCW
            grid[(x, y)] = CCW_COL; grid[(x, y + 1)] = CCW_COL
            y += 1; x += 1; dx, dy = 1, 0
            Hmax = max(Hmax, y); continue
        grid[(x, y)] = COL[prog[i]]; i += 1         # place a command
        Hmax = max(Hmax, y); x += dx
    # remaining cells of the final leg stay NOP; IP walks off the edge -> halt
    H = Hmax + 1

    im = Image.new('RGB', (W, H), NOP_COL)
    ipx = im.load()
    for (px_, py_), col in grid.items():
        ipx[px_, py_] = col
    if scale > 1:
        im = im.resize((W * scale, H * scale), Image.NEAREST)
    return im


def main(argv):
    ap = argparse.ArgumentParser(description="Brainloller encoder/decoder/interpreter")
    sub = ap.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('run',    help='interpret and execute an image')
    r.add_argument('image'); r.add_argument('-s', '--scale', type=int, default=1)
    d = sub.add_parser('decode', help='print the Brainfuck source of an image')
    d.add_argument('image'); d.add_argument('-s', '--scale', type=int, default=1)
    e = sub.add_parser('encode', help='write Brainfuck into a Brainloller image')
    e.add_argument('src')
    e.add_argument('out', nargs='?', default=None,
                   help='output PNG (default: source name with .png)')
    e.add_argument('-w', '--width', type=int, default=None)
    e.add_argument('-s', '--scale', type=int, default=1)
    a = ap.parse_args(argv)

    if a.cmd == 'run':
        run_bf(decode(a.image, a.scale))
    elif a.cmd == 'decode':
        sys.stdout.write(decode(a.image, a.scale) + '\n')
    elif a.cmd == 'encode':
        out = a.out or (os.path.splitext(a.src)[0] + '.png')
        code = open(a.src).read()
        encode(code, a.width, a.scale).save(out)
        print(f"wrote {out}")

if __name__ == '__main__':
    main(sys.argv[1:])
