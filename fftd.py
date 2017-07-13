import argparse

import numpy as np
import pyaudio

import procon

parser = argparse.ArgumentParser(description='Provide Fast Fourier Transform data.')
parser.add_argument('-B', '--base', dest='base', default=procon.DEFAULT_BASE, help='Base path for data files')
parser.add_argument('-n', '--name', dest='name', default='fft', help='Name of the FFT data file')
parser.add_argument('-W', '--window', dest='window', type=int, default=1024, help='Number of samples in FFT window')
parser.add_argument('-f', '--frames', dest='frames', type=int, default=512, help='Number of frames to read per FFT calculation')
parser.add_argument('-r', '--rate', dest='rate', type=int, default=22050, help='Sample rate of the audio stream')
parser.add_argument('--window-func', dest='window_func', default='blackman', help='Window function in use (see numpy window functions)')
args = parser.parse_args()

print('Latency: {}s'.format(args.window / (2 * args.rate)))
print('Framerate: {}s^-1'.format(args.rate / args.frames))
size = 4 * (args.window // 2 + 1)
print('Datafile Size: {}byte'.format(size))

pa = pyaudio.PyAudio()
st = pa.open(rate=args.rate, channels=1, format=pyaudio.paFloat32, input=True)

buf = np.zeros((args.window,), dtype=np.float32)
out = procon.get(args.name, args.base, size)
winf = getattr(np, args.window_func)(args.window)

frm = 0

while True:
    frames = np.frombuffer(st.read(args.frames), dtype=np.float32)
    buf = np.concatenate((buf, frames))[-args.window:]
    arr = (np.abs(np.fft.rfft(winf * buf)) / args.frames).astype(np.float32)
    #print(len(out[:]), len(arr.tobytes()))
    out[:] = arr.tobytes()
    frm += 1
    print('\r                                        \rFrame: {}'.format(frm), end='')
