import math, colorsys, argparse

import numpy as np

import procon, util

parser = argparse.ArgumentParser(prog='spectrum', description='Spectrum histogram module (log-log).')
parser.add_argument('-B', '--base', dest='base', default='/tmp/render', help='Base path for data files')
parser.add_argument('-n', '--name', dest='name', default='fft', help='Name of data file (normally FFT)')
parser.add_argument('--intensity-exp', dest='intensity_exp', type=float, default=2, help='Exponent of intensity in luminance calculation; increases contrast between high and low intensities')
parser.add_argument('--hue-exp', dest='hue_exp', type=float, default=0.66, help='Hue exponent; changes the position of the "red end" of the spectrum')
parser.add_argument('--freq-exp', dest='freq_exp', type=float, default=0.5, help='Frequency (X-axis) exponent; values <1 expand the low end and compress the high end, >1 does the opposite')
parser.add_argument('--y-exp', dest='y_exp', type=float, default=1, help='Intensity (Y-axis) exponent; values <1 expand lower intensities and compress higher intensities, >1 does the opposite')
parser.add_argument('--min-clip', dest='min_clip', type=float, default=-100, help='Clamped absolute minimum')
parser.add_argument('--max-clip', dest='max_clip', type=float, default=100, help='Clamped absolute maximum')
parser.add_argument('--top-val', dest='top_val', type=float, default=0, help='Value represented at the top of the graph')
parser.add_argument('--range', dest='range', type=float, default=5, help='Range represented vertically in the graph')
args = parser.parse_args([])

def take_args(argv):
    global args
    args = parser.parse_args(argv)

data = procon.get('fft')

@util.memoized
def map_x(i):
    return np.log2(i+1)**args.freq_exp

def map_col(i, intensity):
    return [max(0, min(255, int(255 * cmp))) for cmp in colorsys.hls_to_rgb(0.66 * (i ** args.hue_exp), 0.5 * intensity**args.intensity_exp, 1)]

def render(surf):
    w, h = surf.get_size()
    raw = np.frombuffer(data[:], dtype=np.float32)
    values = np.clip(np.log10(raw), args.min_clip, args.max_clip)
    for idx, v in enumerate(values):
        if math.isnan(v):
            v = args.min_clip
        frac, fracn = idx / len(values), (idx + 1) / len(values)
        x, xn = w * map_x(frac), w * map_x(fracn)
        y = h * (args.top_val - (v / args.range))
        ny = (h - y) / h
        col = map_col(frac, ny)
        if args.y_exp != 1:
            if ny < 0:
                continue
            y = int(h * (1 - ny ** args.y_exp))
        surf.fill(col, (x, y, xn - x, h - y))
