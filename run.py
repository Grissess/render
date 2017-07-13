import argparse, sys

import pygame

parser = argparse.ArgumentParser(description='Run a render module.')
parser.add_argument('module', nargs=argparse.REMAINDER)
args = parser.parse_args()

pygame.init()
W, H = pygame.display.list_modes()[0]
disp = pygame.display.set_mode((W, H), pygame.FULLSCREEN|pygame.DOUBLEBUF|pygame.HWSURFACE)
clock = pygame.time.Clock()

mod = __import__(args.module[0])
mod.take_args(args.module[1:])

while True:
    for ev in pygame.event.get():
        if ev.type == pygame.KEYDOWN and ev.key == pygame.K_q:
            exit()
    disp.fill((0, 0, 0))
    mod.render(disp)
    pygame.display.flip()
    clock.tick(60)
