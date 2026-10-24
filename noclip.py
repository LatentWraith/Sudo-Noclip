from __future__ import annotations
from typing import cast
import time
import os
import random
import shutil
import math
import sys
from numba import njit, prange
import numpy as np
from functools import lru_cache

class Terminal:
    def __init__(self):
        self.plat = sys.platform
        self.fd = None
        self.orig = None
        
        if self.plat != "win32":
            import termios
            import tty
            
            self.fd = sys.stdin.fileno()
            self.orig = termios.tcgetattr(self.fd)
            tty.setcbreak(self.fd)
    
    def hide(self):
        print("\033[?25l", end="", flush=True)
        
    def show(self):
        print("\033[?25h", end="", flush=True)
        self.restore()
        
    def restore(self):
        if self.plat != "win32" and self.fd is not None and self.orig is not None:
            import termios
            try:
                termios.tcsetattr(self.fd, termios.TCSADRAIN, self.orig)
            except Exception:
                pass
            
    def get_char(self) -> str:
        if sys.platform == "win32":
            import msvcrt
            if msvcrt.kbhit():
                ch = msvcrt.getch()
                while msvcrt.kbhit():
                    msvcrt.getch()
                return ch.decode("utf-8", errors="ignore")
            return ""
        else:
            import select
            import termios

            if self.fd is not None and select.select([self.fd], [], [], 0)[0]:
                ch = os.read(self.fd, 1).decode("utf-8", errors="ignore")
                termios.tcflush(self.fd, termios.TCIFLUSH)
                return ch
            return ""

class Matrix():
    def __init__(self, raw: list[list[float]], angle: float | None = None):
        if angle is not None:
            self.raw = [[math.cos(angle), -math.sin(angle)],
                        [math.sin(angle), math.cos(angle)]]
        else:
            self.raw = raw
        
    def __matmul__(self, other: Matrix | Vec): # type: ignore
        if isinstance(other, Vec):
            out = (self.raw[0][0] * other.raw[0] + self.raw[0][1] * other.raw[1], self.raw[1][0] * other.raw[0] + self.raw[1][1] * other.raw[1])
            return Vec(out)
        else:
            out = [[self.raw[0][0] * other.raw[0][0] + self.raw[0][1] * other.raw[1][0], self.raw[0][0] * other.raw[0][1] + self.raw[0][1] * other.raw[1][1]],
                   [self.raw[1][0] * other.raw[0][0] + self.raw[1][1] * other.raw[1][0], self.raw[1][0] * other.raw[0][1] + self.raw[1][1] * other.raw[1][1]]]
            return Matrix(out)

class Vec():
    def __init__(self, raw: tuple[float, float]):
        self.raw = raw
        
    def __mul__(self, other: float):
        return Vec((self.raw[0] * other, self.raw[1] * other))

    def __add__(self, other):
        return Vec((self.raw[0] + other.raw[0], self.raw[1] + other.raw[1]))
    def __sub__(self, other):
        return Vec((self.raw[0] - other.raw[0], self.raw[1] - other.raw[1]))
    
def col(x: str, r: float, g: float, b: float, block: bool = False) -> str:
    return f"\033[{48 if block else 38};2;{min(255, round(r))};{min(255, round(g))};{min(255, round(b))}m{x}\033[0m"

def clear():
    os.system("clear" if sys.platform!="win32" else "cls")
    
def guide(term: Terminal):
    clear()
    
    out = col("[GUIDE]", 255, 0, 0)
    out+="\n\n"+col("[1]", 255, 255, 0)+"\tFear\n"+col("[2]", 255, 255, 0)+"\tStability\n"+col("[3]", 255, 255, 0)+"\tCorrupted Fragments\n"+col("[4]", 255, 255, 0)+"\tPockets\n"+col("[5]", 255, 255, 0)+"\tRifts\n"+col("[6]", 255, 255, 0)+"\tTrapped Rifts\n\n"+col("[7]", 255, 255, 0)+"\tBack\n"+"\n\nSelect an option (1-7)"
    
    for ch in out:
        print(ch, end="", flush=True)
        time.sleep(0.005)
        
    while True:
        try:
            opt = min(max(int(term.get_char()), 1), 7)
            clear()
            match opt:
                case 1:
                    out = col("[FEAR]", 255, 0, 0)
                    out+="\n\nFear is a metric influenced by anomalies and entities.\nIt can be used to navigate safely.\nAs a rule of thumb: if your Fear spikes whilst exploring in a direction, "+col("turn back immediately.", 255, 0, 0)
                case 2:
                    out = col("[STABILITY]", 255, 0, 0)
                    out+="\n\nThe Dimension Stability indicates the structural integrity of your current dimension.\nIf your presence drives the dimension into instability, the "+col("?????????", 255, 0, 0)+" will rip, causing a Rift to form and the dimension to corrupt.\n."
                    out+="An unstable dimension may show signs of corruption prior to tearing, repairing itself once relieved of human influence."
                case 3:
                    out = col("[CORRUPTED FRAGMENTS]", 255, 0, 0)
                    out+="\n\nCorrupted Fragments are notes left behind by past visitors.\nDue to their time spent in the "+col("?????????", 255, 0, 0)+", these notes are often fragmented and corrupted, hence the name."
                    out+="\nFinding and recovering these yields information about the past experiences of others, which may be useful."
                case 4:
                    out = col("[POCKETS]", 255, 0, 0)
                    out+="\n\nPockets are spatial anomalies containing items left behind by previous visitors.\nAppearing as jagged tears in the world's geometry, they mimic the colour of adjacent walls yet possess a visibly distorted and unnatural form."
                    out+="\nThey react to the physical proximity of a human, opening automatically when approached."
                case 5:
                    out = col("[RIFTS]", 255, 0, 0)
                    out+="\n\nRifts are physical tears in the "+col("?????????", 255, 0, 0)+", caused when a Dimension becomes unstable due to human presence.\nUnlike Pockets, Rifts take on a blinding white colour and serve as doorways to other dimensions."
                    out+="\nIn the past, Rifts required decades to form due to the immense stability of the "+col("?????????", 255, 0, 0)+".\nHowever, as of late, Rifts have begun occurring alarmingly often; the cause remains unknown."
                case 6:
                    out = col("[TRAPPED RIFTS]", 255, 0, 0)
                    out+="\n\nTrapped Rifts appear identical to Rifts when viewed from afar, but drastically change colour when approached.\nThese form when an organic anomaly is forced to tear open a dimension, typically by a higher power."
                    out+="\nAlthough rare, one would still advise caution towards Rifts in the event that they are traps."
                case 7:
                    clear()
                    return
            out+="\n\n\nPress "+col("[B]", 255, 255, 0)+" to return to the Main Menu."
            for ch in out:
                print(ch, end="", flush=True)
                time.sleep(0.005)
                
            while term.get_char().lower()!="b":
                time.sleep(0.05)
            clear()
            return
        except:
            pass
        
    clear()

def help(term: Terminal):
    clear()
    
    out = col("[HELP]", 255, 0, 0)
    out+="\n\nControls:\nUse the "+col("[WASD]", 0, 255, 0)+" keys to move around,\n"+col("[O]", 0, 255, 0)+" to turn to the left,\nand "+col("[P]", 0, 255, 0)+" to turn to the right.\nTravelling through water will cause you to move slower."
    out+="\n\nStatus Bar:\nThe Status Bar at the bottom of the display tracks vital information.\nIt displays core controls, technical info, "+col("[Fear]", 0, 255, 0)+" Level, and Dimension "+col("[Stability]", 0, 255, 0)+"."
    out+="\n\nObjective:\nYou have noclipped into the "+col("?????????", 255, 0, 0)+" and must find a way out.\nSurvive the "+col("??????", 255, 0, 0)+", recover information, and find Rifts to navigate your way out."
    out+="\n\n\nPress "+col("[B]", 255, 255, 0)+" to return to the Main Menu."

    for ch in out:
        print(ch, end="", flush=True)
        time.sleep(0.005)
        
    while term.get_char().lower()!="b":
        time.sleep(0.05)
    clear()
    
sett = {"raycast": 8, "quant": 1/128}

def settings(term: Terminal):
    clear()
        
    out = col("[SETTINGS]", 255, 0, 0)
    out+="\n\nThis is a very CPU-intensive game. Adjust your settings accordingly.\n\n"+col("[1]", 255, 255, 0)+"\tRaycasting\n"+col("[2]", 255, 255, 0)+"\tColour Quantisation\n\n"+col("[3]", 255, 255, 0)+"\tBack"
    
    for ch in out:
        print(ch, end="", flush=True)
        time.sleep(0.005)
        
    while True:
        try:
            opt = min(max(int(term.get_char()), 1), 3)
            clear()
            key = "raycast"
            values = []
            match opt:
                case 1:
                    out = col("[RAYCASTING]", 255, 0, 0)
                    out+="\n\nRaycasting is how this game renders scenes.\nThis setting controls how precise the raycasting is.\nA lower setting increases performance at the cost of aliasing.\n\n"
                    out+=col("[1]", 255, 255, 0)+"\t4 (Fastest)\n"+col("[2]", 255, 255, 0)+"\t8\n"+col("[3]", 255, 255, 0)+"\t16\n"+col("[4]", 255, 255, 0)+"\t32 (Highest Quality)\n\n"+col("[5]", 255, 255, 0)+"\tBack"
                    key = "raycast"
                    values = [4, 8, 16, 32]
                case 2:
                    out = col("[COLOUR QUANTISATION]", 255, 0, 0)
                    out+="\n\nThis game uses ANSI escape codes to colour individual characters for pixels.\nANSI colours are expensive on CPU (irrelevant if you are on a GPU accelerated terminal),\nso near-identical colours are merged to increase performance.\n"
                    out+="Increasing this setting increases the total amount of colour shades\nthat can be displayed, at the cost of performance.\n\n"
                    out+=col("[1]", 255, 255, 0)+"\t32 Shades\n"+col("[2]", 255, 255, 0)+"\t64 Shades\n"+col("[3]", 255, 255, 0)+"\t128 Shades\n"+col("[4]", 255, 255, 0)+"\t256 Shades\n\n"+col("[5]", 255, 255, 0)+"\tBack"
                    key = "quant"
                    values = [1/32, 1/64, 1/128, 1/256]
                case 3:
                    clear()
                    return
            for ch in out:
                print(ch, end="", flush=True)
                time.sleep(0.005)
                
            while True:
                char = term.get_char()
                match char.lower():
                    case "1":
                        sett[key] = values[0]
                        break
                    case "2":
                        sett[key] = values[1]
                        break
                    case "3":
                        sett[key] = values[2]
                        break
                    case "4":
                        sett[key] = values[3]
                        break
                    case "5":
                        break
            clear()
            return
        except:
            pass
    
def credits(term: Terminal, rand: list[str]):
    clear()
    
    while term.get_char().lower()!="b":
        print("\033[1;1H")
        out = "[CREDITS]"
        out+="\n\n\n"+col("Made by:\t", 40, 0, 255)+col(random.choice(rand)+random.choice(rand)+random.choice(rand)+random.choice(rand), 135, 0, 255)+col("[STEFAN LUPASCU]", 40, 0, 255)+col(random.choice(rand)+random.choice(rand)+random.choice(rand)+random.choice(rand), 135, 0, 255)
        out+="\n\n\nPress "+col("[B]", 255, 255, 0)+" to return to the Main Menu."
        
        print(out, end="", flush=True)
        
        time.sleep(0.05)
    clear()

def menu(rand: list[str], term: Terminal):
    clear()
    print()
    
    while True:
        print("\033[1;1H", end="")
        out = col(f"{random.choice(rand)}{random.choice(rand)}{random.choice(rand)}[SUDO NOCLIP]{random.choice(rand)}{random.choice(rand)}{random.choice(rand)}", 255, 0, 0)
        out+="\n\n"+col("[1]", 255, 255, 0)+"\tPlay\n"+col("[2]", 255, 255, 0)+"\tGuide\n"+col("[3]", 255, 255, 0)+"\tHelp\n"+col("[4]", 255, 255, 0)+"\tSettings\n"+col("[5]", 255, 255, 0)+"\tCredits\n\n"+col("[6]", 255, 255, 0)+"\tQuit"+"\n\n\nSelect an option (1-6)"
        print(out, end="", flush=True)
        
        try:
            opt = min(max(int(term.get_char()), 1), 6)
            match opt:
                case 1:
                    clear()
                    return
                case 2:
                    guide(term)
                case 3:
                    help(term)
                case 4:
                    settings(term)
                case 5:
                    credits(term, rand)
                case 6:
                    term.show()
                    sys.exit()
        except Exception:
            pass
        
        time.sleep(0.05)

def read_note(num: str, lines: list[str]):
    clear()
    print("\033[1;1H")
    print()
    time.sleep(2)
        
    for ch in f"[RECOVERING CORRUPTED FRAGMENT: ANONYMOUS_USER_0-X{num}]":
        print("\033[3m"+ch+"\033[0m", end="", flush=True)
        if ch!=" ": time.sleep(0.2)
    time.sleep(0.5)
        
    print()
    print()
    for line in lines:
        for ch in line:
            print(col(ch, 255, 255, 0), end="", flush=True)
            if ch!=" ": time.sleep(0.2)
        time.sleep(0.5)
        print()
    print()
    time.sleep(4)

def load(width: int, heigth: int, term: Terminal):
    rand = [chr(x) for x in range(33, 127)]
    menu(rand, term)
    
    def skip():
        if term.get_char()=="x":
            print()
            return 1/0
        
    print()
    print("Press x to skip intro")
    print()
    opt = ["   ", ".  ", ".. ", "..."]
    for _ in range(4):
        skip()
        for suff in opt:
            print("\rLoading"+suff, end="")
            time.sleep(0.25)
    
    gl = 72
    for i in range(gl):
        skip()
        out = ""
        for ch in "Loading"+opt[i%4]:
            chan = (i/(gl-1))**3
            if random.random()>chan:
                out+=ch
            else:
                out+=col(random.choice(rand), 255, 0, 0)
                    
        print("\r\033[K"+out+"\t"+out+"\t"+out, end="", flush=True)
        time.sleep(0.05+((1-(i/(gl-1))) * 0.15))
    
    for _ in range(16):
        skip()
        out = ""
        for _ in range(width):
            out+=random.choice(rand)
        print("\r\033[K"+col(out, 255, 0, 0), end="", flush=True)
        time.sleep(0.04)
        
    for _ in range(16):
        skip()
        out = ""
        for _ in range(heigth):
            for _ in range(width):
                out+=random.choice(rand)
            out+="\n"
        out = out[:-2]
        print("\r\033[K"+col(out, 255, 0, 0), end="", flush=True)
        time.sleep(0.04)
    skip()
    
    clear()
    time.sleep(1.5)
    
    print()
    for ch in "Greetings, Traveller.":
        skip()
        print(col(ch, 0, 180, 200), end="", flush=True)
        if ch!=" ": time.sleep(0.2)
    print("\n")
    for ch in "Trust your heart":
        skip()
        print(col(ch, 0, 180, 200), end="", flush=True)
        if ch!=" ": time.sleep(0.2)
    print(col(".", 255, 0, 0), end="", flush=True)
    print()
    for ch in "Stay in the light":
        skip()
        print(col(ch, 0, 180, 200), end="", flush=True)
        if ch!=" ": time.sleep(0.2)
    print(col(".", 255, 0, 0), end="", flush=True)
    print()
    for ch in "Do not close your eyes":
        skip()
        print(col(ch, 0, 180, 200), end="", flush=True)
        if ch!=" ": time.sleep(0.2)
    print(col(".", 255, 0, 0), end="", flush=True)
    print()
    for ch in "Do not let your light go out":
        skip()
        print(col(ch, 0, 180, 200), end="", flush=True)
        if ch!=" ": time.sleep(0.2)
    for ch in "...":
        print(col(ch, 255, 0, 0), end="", flush=True)
        time.sleep(1.5)
    print()
    
    read_note("0000", ["My heart sank at the truth,", "That darkness was no fleeting guest.", "My eyes pleaded for an escape,", "But the light offered me none."])

    clear()

def gen_maze(nx: int, ny: int, scale: int, loop: float) -> tuple[np.ndarray, tuple[float, float], np.ndarray, np.ndarray, np.ndarray]:
    def is_valid(x: list) -> bool:
        return x[0]>0 and x[0]*2<nx and x[1]>0 and x[1]*2 <ny
    
    out = []
    mask = []
    lights = []
    entity = [9999, 9999]
    for _ in range(ny):
        row = []
        for _ in range(nx):
            row.append(1)
        out.append(row)
    for _ in range(ny//2):
        row = []
        for _ in range(nx//2):
            row.append(0)
        mask.append(row)
    
    start = [nx//4, ny//4]
    stack = [start]
    mask[start[1]][start[0]] = 1
    
    dirs = [[0,1],[0,-1],[1,0],[-1,0]]
    while stack:
        node = stack[-1]
        
        options = []
        for d in dirs:
            o = [node[0]+d[0], node[1]+d[1]]
            if is_valid(o) and (mask[o[1]][o[0]] == 0 or (random.random()<loop)):
                options.append(o)
        if not options:
            stack.pop()
            continue
        
        n = random.choice(options)
        mask[n[1]][n[0]] = 1
        
        cx, cy = node[0]*2, node[1]*2
        tx, ty = n[0]*2, n[1]*2
        
        fx, fy = cx+((tx-cx)//2), cy+((ty-cy)//2)
        out[cy][cx] = 0
        out[ty][tx] = 0
        out[fy][fx] = 0
        
        shift = (scale-1) /2
        lights.append((fx*scale + shift, fy*scale + shift))
        
        entity[0], entity[1] = (cx, cy) if cy<entity[1] else (entity[0], entity[1])
        stack.append(n)

    expanded = []
    for row in out:
        expanded_row = [cell for cell in row for _ in range(scale)]
        expanded.extend([expanded_row.copy() for _ in range(scale)])
    
    clear()
    return (np.array(expanded), (entity[0] * scale, entity[1] * scale), np.array(out), np.array(lights), np.zeros((nx*ny*scale*scale, 3), dtype=np.int32))

@njit(fastmath=True, cache=True, boundscheck=False)
def pathfind(grid: np.ndarray, target: tuple[float, float], origin: tuple[float, float], stack: np.ndarray, width: int, height: int) -> tuple[int, int]:
    out = np.full((height, width), -1, dtype=np.int32)
    
    tx, ty = round(target[0]), round(target[1])
    ox, oy = round(origin[0]), round(origin[1])

    if (ox, oy) == (tx, ty):
        return (ox, oy)
    
    out[oy][ox] = 0
    
    stack_top = 0
    stack[0] = (ox, oy, 3)
    
    dirs = ((0, 1), (0, -1), (1, 0), (-1, 0))
    while len(stack)>0:
        cx, cy, dist = stack[stack_top]
        stack_top-=1
        dist+=1
        
        for (dx, dy) in dirs:
            nx, ny = cx + dx, cy + dy
            if out[ny][nx]==-1:
                
                if grid[ny][nx] == 0 or (nx == tx and ny == ty):
                    out[ny][nx] = dist

                    stack[stack_top+1] = nx, ny, dist
                    stack_top+=1
                
                    if nx == tx and ny == ty:
                        return (cx, cy)
    return (-1, -1)

@njit(fastmath=True, cache=True, boundscheck=False)
def raycast(dir: tuple[float, float], grid: np.ndarray, origin: tuple[float, float], max_dist: float, mini: int, l: int, level: int, mask: np.ndarray, scale: int) -> tuple[bool, float]:
    steps = 1
    while True:
        if steps>= max_dist*mini:
            break
        
        sdivm = steps/mini
        px, py = origin[0] + (dir[0] * (sdivm)), origin[1] + (dir[1] * (sdivm))
        x, y = round(px), round(py)
        
        if px < 0 or py < 0 or px >= l or py >= l:
            return (False, 1.0)
        
        if level!=4:
            cx, cy = int(px // scale), int(py // scale)
            sx, sy = cx*scale, cy*scale
            if mask[cy][cx] == 0:
                dy = (((sy+scale - py) if dir[1]>0 else (py-sy)) / abs(dir[1])) if dir[1]!=0 else 99999.0
                dx = (((sx+scale - px) if dir[0]>0 else (px-sx)) / abs(dir[0])) if dir[0]!=0 else 99999.0
                
                steps += round(min(dy, dx)*mini) + 1
                continue
                    
        match grid[y][x]:
            case 1:
                return (True, (steps)/(max_dist*mini))
            case 2:
                if level==4:
                    return (True, -10.0)
                else:
                    return (True, -9999.0)
            case 3:
                
                return (True, 0.0)
        steps+=1
        
    return (False, 1.0)

@njit(fastmath=True, cache=True, boundscheck=False, parallel=True)
def ray_trace(grid: np.ndarray, mask: np.ndarray, scale:int, lights: np.ndarray, light_str: float, light_max: float, kernel: int) -> np.ndarray:
    rt = grid.astype(np.float32)
    
    l = len(rt)
    for y in prange(l):
        for x in range(len(rt[0])):
            if grid[y][x]==1:
                rt[y][x] = 0.0
                continue
            
            shade = 0.0
            for (lx, ly) in lights:
                dx, dy = lx-x, ly-y
                contr, hit = trace_light(dx, dy, x, y, light_max, l, grid, mask, scale)
                shade+=(light_str/contr) if hit else 0.0
            
            rt[y][x] = min(shade, 1.0)
            
    print()
    out = np.zeros((len(rt), len(rt[0])), dtype=np.float32)
    l0, l1 = len(out), len(out[0])
    
    for py in prange(l0):
        for px in range(l1):
            out[py][px] = sample_light(rt, (px, py), kernel, (l0, l1))
            
    return out

@njit(fastmath=True, cache=True, boundscheck=False)
def trace_light(dx: float, dy: float, x: float, y: float, light_max: float, l: int, grid: np.ndarray, mask: np.ndarray, scale: int) -> tuple[float, bool]:
    
    mag = math.sqrt(dx**2 + dy**2) + 1e-6
    nx, ny = dx/mag, dy/mag
    
    if mag<=light_max:
        hit, _ = raycast((nx, ny), grid, (x, y), mag+0.001, 1, l, 0, mask, scale)
        if not hit:
            return (1 + mag**2, True)
        
    return (0.0, False)

@njit(fastmath=True, cache=True, boundscheck=False)
def sample_light(lightmap: np.ndarray, pos: tuple, kernel: int, dim: tuple[int, int]) -> float:
    l = dim[0]
    l1 = dim[1]
    
    shade = 0.0
    n = 0
    
    for dy in range(-kernel, kernel+1):
        for dx in range(-kernel, kernel+1):
            x, y = round(pos[0]+dx), round(pos[1]+dy)
            if 0<=y<l and 0<=x<l1:
                s = float(lightmap[y][x])
                if s>0.0:
                    n+=1
                    shade+= s
    
    return 0.0 if n==0 else shade/n

@njit(fastmath=True, cache=True, boundscheck=False)
def raster(
        ct: float,
        columns: np.ndarray,
        floor_col: tuple[int, int, int],
        roof_col: tuple[int, int, int],
        half: float,
        wall_proj: float,
        player: tuple[float, float],
        grid_n: int,
        lm: np.ndarray | None,
        gamma: float,
        quantise: float,
        in_water: bool,
        wet_wall: float,
        ao: float,
        water_shine: float,
        wave_shade: float,
        wave_freq: float,
        wave_speed: float,
        move_ema: float,
        global_shade: float,
        grad: float,
        js: bool,
        width: int,
        height: int,
        render_dist: int,
        ambient: float,
    ) -> np.ndarray:
    out = np.zeros((height, width, 3), dtype=np.int32)
    
    for y in range(height):
        refl_fade = (1.0 - (y-half)/((height-1) -half)) ** 2
        
        dy = max(abs(y-half), 0.5)
        d = max(wall_proj * height/(2*dy), 0.25) /render_dist
        
        base_eff = (max(0.0, 1-d)**2.0) * global_shade * grad
        
        is_roof = y < half
        base = roof_col if is_roof else floor_col
        wave = 1.0
        if (not is_roof) and in_water:
            wave -= wave_shade * (1-refl_fade) * move_ema *(math.sin(y*wave_freq+ct*wave_speed) ** 2)
        base_floor = (round(base[0]*wave), round(base[1]*wave), round(base[2]*wave))
        
        for px, (hit, top, bottom, wall0, wall1, wall2, ray_dir0, ray_dir1, ray_dist) in enumerate(columns):
            top = int(top)
            bottom = int(bottom)

            if js:
                if wall0==0.0 and wall1==0.0 and wall2==0.0:
                    if y==height//2 and ((px==width//2 +1) or (px==(width//2 -1))):
                        out[y][px] = (255, 255, 255)
                        continue

            floor_dist = max(0.0, d * ray_dist - 2.0)
            hx = round(player[0] + ray_dir0 * floor_dist)
            hy = round(player[1] + ray_dir1 * floor_dist)

            if lm is not None and 0<=hy<grid_n and 0<=hx<grid_n:
                light = float(lm[hy][hx] * (1-d))
            else:
                light = 1.0

            eff = round((base_eff * max(ambient, light) *gamma) / quantise) * quantise

            floor = (round(base_floor[0]*eff), round(base_floor[1]*eff), round(base_floor[2]*eff))

            if (hit==1.0) and top <= y <= bottom:
                if (not (top <= y-1 <= bottom)) or (not (top <= y+1 <= bottom)):
                    if in_water and y>half:
                        colour = (wall0*wet_wall + base_floor[0]*(1-wet_wall)*eff, wall1*wet_wall + base_floor[1]*(1-wet_wall)*eff, wall2*wet_wall + base_floor[2]*(1-wet_wall)*eff)
                    else:
                        colour = (wall0*ao, wall1*ao, wall2*ao)
                else:
                    colour = (wall0, wall1, wall2)
            else:
                if ((top <= y-1 <= bottom) or (top <= y+1 <= bottom)) and not in_water:
                    colour = (base[0]*eff*ao, base[1]*eff*ao, base[2]*eff*ao)
                else:
                    h = bottom
                    ref = round(h-(y-h))
                    if in_water and (ref>=0) and (not is_roof) and (ref<y):
                        sr, sg, sb = out[ref][px]

                        shine = water_shine * refl_fade
                        colour = (sr*shine + floor[0]*(1-shine), sg*shine + floor[1]*(1-shine), sb*shine + floor[2]*(1-shine))
                    else:
                        colour = floor
            
            out[y][px][0] = min(255, round(colour[0]))
            out[y][px][1] = min(255, round(colour[1]))
            out[y][px][2] = min(255, round(colour[2]))
        
    return out

@lru_cache(maxsize=2**15)
def get_ansi(r: int, g: int, b: int, glyph: str) -> str:
    return f"\033[38;2;{r};{g};{b}m{glyph}"

class Theme():
    def __init__(self, wall: tuple[int, int, int], floor: tuple[int, int, int], roof: tuple[int, int, int]):
        self.wall = wall
        self.floor = floor
        self.roof = roof
    def update(self, wall: tuple[int, int, int], floor: tuple[int, int, int], roof: tuple[int, int, int]):
        self.wall = wall
        self.floor = floor
        self.roof = roof

class State():
    def __init__(self, grid: int):
        width, height = shutil.get_terminal_size(fallback=(80, 24))
        self.width = width
        self.height = height
        
        self.term = Terminal()
        self.term.hide()
        
        try:
            load(width, height, self.term)
        except Exception:
            pass
        
        clear()
        
        self.in_grid = grid
        self.rand = [chr(x) for x in range(33, 127)]
        
        self.scale = 8
        self.grid, entity, self.mask, self.lights, self.stack = gen_maze(grid, grid, self.scale, 0.1)
        self.grid_n = len(self.grid)
        
        self.player = Vec((self.scale * (grid // 2) + 1, self.scale * (grid // 2) + 1))
        self.view = Matrix([], angle=0)
        self.fov = math.radians(90)
        self.left = Matrix([], angle=math.radians(-15))
        self.right = Matrix([], angle=math.radians(15))
        
        self.walk_speed = 0.7
        self.water_speed = 0.45
        self.in_water = False
        
        self.render_dist = 32
        self.sub_steps = int(sett["raycast"])
        self.global_shade = 0.8
        self.eff_exp = 1.0
        self.wall_proj = 5.0
        
        self.entity = Vec(entity)
        self.entity_step = 0.07
        
        self.theme = Theme((228, 230, 168), (156, 147, 88), (207, 204, 162))
        self.rand = [chr(x) for x in range(33, 127)]
        self.quantise = float(sett["quant"])
        
        self.horizon_fac = 0.5
        self.wobble = 0.05
        self.move_ema = 1.0
        self.ema_fac = 0.8
        self.wob_fac = 16.0
        self.wob_ema = 0.0
        self.wob_ema_fac = 0.6
        
        self.ao = 0.92
        self.wet_wall = 0.75
        self.water_shine = 0.7
        
        self.light_strength = 6.0
        self.light_off = 0.01
        self.ambient = 0.1
        self.light_max = math.sqrt((self.light_strength/self.light_off) - 1)
        self.blur_kernel = 2
        
        print("Lighting the map", flush=True)
        print()
        print("Ray Tracing...", flush=True)
        self.lm = ray_trace(self.grid, self.mask, self.scale, self.lights, self.light_strength, self.light_max, self.blur_kernel)
        
        self.wave_shade = 0.85
        self.wave_speed = 2.75
        self.wave_freq = 3.55
        
        self.js_every = 30.0
        self.js_jitter = 5.0
        self.next_js = time.time()+(random.random()*self.js_jitter*2 + (self.js_every-self.js_jitter))
        self.since_js = -1.0
        self.js_time = 0.2
        self.js = False
        
        self.glyphs = ["█"]
        self.death_glyphs = ["▓", "░"]
        self.mac = False
        
        self.escape = False
        self.level = 1
        self.rift = Vec((-999, -999))
        self.flash = False
        
        self.angles = [Vec((math.cos(((i/(self.width- 1)-0.5)) * self.fov), math.sin(((i / (self.width-1)- 0.5)) * self.fov)))for i in range(self.width)]
        
        self.fps = 60
        self.rift_time = 220
        self.since_rift = time.time()
        
        self.DEV = False
        
        self.pocket_every = 40
        self.pocket = Vec((-999, -999))
        self.since_pocket = time.time()
        self.pocket_n = -1
        self.pockets_l1 = [
            [
                "I swear I've been here before.",
                "Have I been going round in circles? No, not possible.",
                "Surely not?"
            ],
            [
                "I measured this corridor.",
                "Forty paces long an hour ago. Now it's sixty.",
                "Stop looking at the corners."
            ],
            [
                "Don't look at the lights.",
                "They ain't wired to no power.",
                "They buzz and pulse like open eyes.",
                "When the eyes die out, run."
            ],
            [
                "One step, two step, three step, four.",
                "Five step, six step, seven...?",
                "They're not mine.",
                "THEY'RE NOT..."
            ],
            [
                "If Fair is Foul,",
                "And Foul is Fair",
                "Why are the walls filthy,",
                "As well as the air?"
            ],
        ]
        self.p_nums_1 = ["1A4F", "28B3", "3F7C", "48A1", "5D2E"]
        self.p_nums_2 = ["8142", "9C55", "A38F", "B1C6", "C409"]
        self.p_nums_3 = ["E831", "F10A", "F5C4", "FA88", "FFFF"]
        self.p_notes = 5
        self.pockets_l2 = [
            [
                "Dutch? Is this Tahiti?"
            ],
            [
                "You Sir, are a Fish."
            ],
            [
                "Silver for monsters. Steel for humans. Water for...",
                "What do I draw for shadows?"
            ],
            [
                "Geppetto, where art thou?",
                "Is that you?",
                "Or is that me?",
            ],
            [
                "GET OUT OF MY SWAMP!"
            ],
        ]
        self.pockets_l3 = [
            [
                "i am sane i am sane i am sane i am sane",
                "i am sane i am sane i am sane i am sane",
                "i am sane i am sane i am sane"
            ],
            [
                "Always wait thirty minutes after swimming before eating.",
                "What's the time Mister Wolf?"
            ],
            [
                "Look! Look at the funny one hiding behind the pillar!"
            ],
            [
                "Wake up Samurai,",
                "We have a city to poke.",
                "Wait, come back!"
            ],
            [
                "If he be Mister Hyde,", "then I shall be Mister Seek!"
            ],
        ]
        
    def lose(self):
        print("\033[1;1H")
        out = ""
        for _ in range(self.height):
            for _ in range(self.width):
                out+=random.choice(self.rand)
            out+="\n"
        out = out[:-2]
        print(col(out, 255, 0, 0), end="", flush=True)
        time.sleep(3)
        
        print("\033[999;999H")
        print("\n\n")
        time.sleep(2)
        for ch in "Your heart falls silent":
            print(ch, end="", flush=True)
            if ch!=" ": time.sleep(0.1)
        print(col(".", 255, 0, 0), end="", flush=True)
        time.sleep(0.25)
        
        print()
        for ch in "You step into the darkness":
            print(ch, end="", flush=True)
            if ch!=" ": time.sleep(0.1)
        print(col(".", 255, 0, 0), end="", flush=True)
        time.sleep(0.25)
                
        print()
        for ch in "You close your eyes":
            print(ch, end="", flush=True)
            if ch!=" ": time.sleep(0.1)
        print(col(".", 255, 0, 0), end="", flush=True)
        time.sleep(0.25)
        
        print()
        for ch in "Your light flickers":
            print(ch, end="", flush=True)
            if ch!=" ": time.sleep(0.1)
        for ch in " ... ":
            print(col(ch, 255, 0, 0), end="", flush=True)
            time.sleep(0.1)
        
        for ch in "then fades":
            print(ch, end="", flush=True)
            if ch!=" ": time.sleep(0.1)
        print(col(".", 255, 0, 0), flush=True)
        time.sleep(0.5)
        
        print()
        for ch in "Until we meet again, fellow Traveller":
            print(ch, end="", flush=True)
            if ch!=" ": time.sleep(0.2)
        for ch in "...":
                print(col(ch, 255, 0, 0), end="", flush=True)
                time.sleep(0.5)
        print()
        print()
        
        sys.tracebacklimit = 0
        raise ConnectionError("\n[Exit Code: 404 - Connection Lost: Gateway timed out. Host is no longer responding.]")
    
    def win(self):
        clear()
        print("\033[1;1H")
        print()
        time.sleep(5)
        
        for ch in "Our hearts knew you would come":
            print(col(ch, 0, 180, 200), end="", flush=True)
            if ch!=" ": time.sleep(0.2)
        print(col(".", 255, 0, 0), flush=True)
        time.sleep(0.5)
        
        for ch in "The darkness is too vast alone":
            print(col(ch, 0, 180, 200), end="", flush=True)
            if ch!=" ": time.sleep(0.2)
        print(col(".", 255, 0, 0), flush=True)
        time.sleep(0.5)
        
        for ch in "Our eyes watched you reach for the light":
            print(col(ch, 0, 180, 200), end="", flush=True)
            if ch!=" ": time.sleep(0.2)
        print(col(".", 255, 0, 0), flush=True)
        time.sleep(0.5)
        
        for ch in "So now we can share yours":
            print(col(ch, 0, 180, 200), end="", flush=True)
            if ch!=" ": time.sleep(0.2)
        for ch in ".":
            print(col(ch, 255, 0, 0), end="", flush=True)
            time.sleep(0.5)
        
        time.sleep(1)
        print()
        print()
        print()
        
        for ch in "Your heart stops its struggle.":
            print(col(ch, 255, 0, 0), end="", flush=True)
            if ch!=" ": time.sleep(0.2)
        time.sleep(0.5)
        
        print()
        for ch in "You join the darkness.":
            print(col(ch, 255, 0, 0), end="", flush=True)
            if ch!=" ": time.sleep(0.2)
        time.sleep(0.5)
        
        print()
        for ch in "You let your eyes rest.":
            print(col(ch, 255, 0, 0), end="", flush=True)
            if ch!=" ": time.sleep(0.2)
        time.sleep(0.5)
        
        print()
        for ch in "Your light flickers ":
            print(col(ch, 255, 0, 0), end="", flush=True)
            if ch!=" ": time.sleep(0.2)
        for ch in "...":
            print(col(ch, 255, 0, 0), end="", flush=True)
            time.sleep(1.0)
        
        for ch in " then spreads":
            print(col(ch, 255, 0, 0), end="", flush=True)
            if ch!=" ": time.sleep(0.2)
        time.sleep(0.5)
        for ch in "...":
                print(col(ch, 255, 0, 0), end="", flush=True)
                time.sleep(1.0)
        time.sleep(1.0)
        print()
        print()
        sys.tracebacklimit = 0
        raise ConnectionError("\n[Exit Code: 403 - Access Denied]")
     
    def resize(self):
        width, height = shutil.get_terminal_size(fallback=(80, 24))
        if width!=self.width or height!=self.height:
            self.height = height
            self.width = width
            
            self.angles = [Vec((math.cos(((i/(self.width- 1)-0.5)) * self.fov), math.sin(((i / (self.width-1)- 0.5)) * self.fov)))for i in range(self.width)]
            
    def is_valid(self, pos: Vec)-> bool:
        return self.grid[round(pos.raw[1])][round(pos.raw[0])] == 0

    def update(self):
        move = False
        speed = self.water_speed if self.in_water else self.walk_speed
        ch = self.term.get_char()
        
        if ch == "x":
            self.lose()
        if ch == "w":
            new = self.player + (self.view @ Vec((speed, 0)))
            if self.is_valid(new):
                self.player = new
                self.move_ema = self.move_ema * self.ema_fac + (1-self.ema_fac)
                move = True
        elif ch == "a":
            new = self.player + (self.view @ Vec((0, -speed)))
            if self.is_valid(new):
                self.player = new
                self.move_ema = self.move_ema * self.ema_fac + (1-self.ema_fac)
                move = True
        elif ch == "s":
            new = self.player + (self.view @ Vec((-speed, 0)))
            if self.is_valid(new):
                self.player = new
                self.move_ema = self.move_ema * self.ema_fac + (1-self.ema_fac)
                move = True
        elif ch == "d":
            new = self.player + (self.view @ Vec((0, speed)))
            if self.is_valid(new):
                self.player = new
                self.move_ema = self.move_ema * self.ema_fac + (1-self.ema_fac)
                move = True
        if not move:
            self.move_ema*=self.ema_fac
            if self.move_ema < 0.05:
                self.move_ema = 0.0
        if ch == "o":
            self.view = cast(Matrix, self.view @ self.left)
        elif ch == "p":
            self.view = cast(Matrix, self.view @ self.right)
        elif ch == "1":
            self.quantise = 1/32
            self.sub_steps = 4
        elif ch == "2":
            self.quantise = 1/64
            self.sub_steps = 8
        elif ch == "3":
            self.quantise = 1/128
            self.sub_steps = 16
        elif ch == "4":
            self.quantise = 1/256
            self.sub_steps = 32
        
        elif ch == "t":
            if self.mac:
                self.mac = False
                #self.glyphs = ["▉", "█"]
                self.glyphs = ["█"]
            else:
                self.mac = True
                self.glyphs = ["▓", "█"]
                
        line = self.player-self.pocket
        if (math.sqrt(line.raw[0]**2 + line.raw[1]**2))<=2 and self.level!=4:
            s = time.time()
            match self.level:
                case 1:
                    note = self.pockets_l1[self.pocket_n]
                    num = self.p_nums_1[self.pocket_n]
                case 2:
                    note = self.pockets_l2[self.pocket_n]
                    num = self.p_nums_2[self.pocket_n]
                case 3:
                    note = self.pockets_l3[self.pocket_n]
                    num = self.p_nums_3[self.pocket_n]
                case _:
                    note = ["How did you even get this??"]
                    num = "????"
                    
            if not self.DEV: read_note(num, note)
            self.since_rift += (time.time()-s)
            self.since_pocket += (time.time()-s)
            
            self.grid[round(self.pocket.raw[1])][round(self.pocket.raw[0])] = 0
            self.pocket = Vec((-9999, -9999))
        
        line = self.player-self.rift
        if (math.sqrt(line.raw[0]**2 + line.raw[1]**2))<=3 and self.level!=4:
            self.level+=1
            self.escape = False
            self.entity.raw = (9999, 99999)
            self.grid[round(self.rift.raw[1])][round(self.rift.raw[0])] = 1
            self.rift.raw = (9999, 9999)
            
            match self.level:
                case 2:
                    if not self.DEV: read_note("6E90", ["My heart grew sick of the rotting yellow.", "The darkness chased me down the halls.", "My eyes embraced the quiet blue.", "But the unforgiving light chased me still..."])
                    
                    self.theme.update((232, 232, 230), (66, 248, 220), (230, 245, 240))
                    self.render_dist = 128
                    self.horizon_fac = 0.4
                    self.wob_fac = 5.0
                    self.wall_proj = 10.0
                    
                    self.global_shade = 0.9
                    self.ao = 0.95
                    self.light_strength = 8.0
                    self.light_max = math.sqrt((self.light_strength/self.light_off) - 1)
                    
                    self.scale = 16
                    self.grid, entity, self.mask, self.lights, self.stack = gen_maze(self.in_grid, self.in_grid, self.scale, 0.15)
                    self.entity = Vec(entity)
                    self.grid_n = len(self.grid)
                    self.temp = [[-1 for _ in range(self.grid_n)] for _ in range(self.grid_n)]
                    
                    print("Lighting the map", flush=True)
                    print()
                    print("Ray Tracing...", flush=True)
                    self.lm = ray_trace(self.grid, self.mask, self.scale, self.lights, self.light_strength, self.light_max, self.blur_kernel)

                    self.in_water = True
                    self.entity_step = 0.15
                    self.player = Vec((self.scale * (self.in_grid // 2) + 1, self.scale * (self.in_grid // 2) + 1))
                    self.pocket_n=-1
                    
                    clear()
                case 3:
                    if not self.DEV: read_note("D27E", ["My heart had drowned in the pale blue,", "Where clinical white rivalled the dark.", "My eyes had found comfort in the deep,", "Where my fading light fought on..."])
                    
                    self.theme.update((85, 105, 100), (25, 55, 65), (60, 75, 70))
                    self.render_dist = 64
                    
                    self.light_strength = 3.0
                    self.global_shade = 0.8
                    self.blur_kernel = 1
                    self.entity_step = 0.25
                    self.light_max = math.sqrt((self.light_strength/self.light_off) - 1)
                    
                    self.wall_proj = 6.0
                    
                    self.ao = 0.7
                    
                    self.scale = 8
                    self.grid, entity, self.mask, self.lights, self.stack = gen_maze(self.in_grid, self.in_grid, self.scale, 0.15)
                    self.entity = Vec(entity)
                    self.grid_n = len(self.grid)
                    self.temp = [[-1 for _ in range(self.grid_n)] for _ in range(self.grid_n)]
                    
                    
                    print("Lighting the map", flush=True)
                    print()
                    print("Ray Tracing...", flush=True)
                    self.lm = ray_trace(self.grid, self.mask, self.scale, self.lights, self.light_strength, self.light_max, self.blur_kernel)
                    
                    self.player = Vec((self.scale * (self.in_grid // 2) + 1, self.scale * (self.in_grid // 2) + 1))
                    self.pocket_n=-1
                case 4:
                    clear()
                    print("\033[1;1H")
                    print()
                    time.sleep(2)
                    
                    for ch in "[Decoding Incoming Message]":
                        print("\033[3m"+ch, end="", flush=True)
                        time.sleep(0.2)
                        
                    time.sleep(2.0)
                    print()
                    print()
                    for ch in f"RUN":
                        print("\033[3m\033[1m"+col(ch, 255, 0, 0), end="", flush=True)
                        time.sleep(2.0)
                    time.sleep(2.0)
                    
                    self.theme.update((255, 10, 20), (70, 22, 26), (220, 20, 40))
                    self.render_dist = 96
                    self.horizon_fac = 0.5
                    self.wall_proj = 5.0
                    self.wob_fac = 16.0
                    self.ao = 0.1
                    self.lm = None
                    
                    self.fov = math.radians(120)
                    self.angles = [Vec((math.cos(((i/(self.width- 1)-0.5)) * self.fov), math.sin(((i / (self.width-1)- 0.5)) * self.fov)))for i in range(self.width)]
                    
                    self.global_shade = 0.6
                    self.eff_exp = 2.0
                    
                    self.walk_speed = 0.4
                    self.entity_step = 0.3
                    
                    self.scale = 1
                    self.grid = np.array([
                        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                        [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,1],
                        [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,1],
                        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
                        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                        [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,1],
                        [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,1],
                        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                    ])
                    self.view = Matrix([], angle=0)
                    
                    self.grid_n = len(self.grid[0])
                    self.temp = [[-1 for _ in range(self.grid_n)] for _ in range(len(self.grid))]

                    self.in_water = False
                    self.player = Vec((self.grid_n//2, len(self.grid)//2))
                    self.entity = Vec((2, len(self.grid)//2))
                    self.rift = Vec((self.grid_n-1, len(self.grid)//2))
                    
                    self.flash = True
                    
                    clear()
                    
            self.since_rift = time.time()
            self.since_pocket = time.time()
        
        line = self.player-self.entity
        if (math.sqrt(line.raw[0]**2 + line.raw[1]**2))<=2:
            if self.level==4:
                self.win()
            else:
                clear()
                self.lose()
        
    def render(self):
        horiz = ""
        dist = []
        
        line = self.player-self.entity
        grad = (min((math.sqrt(line.raw[0]**self.eff_exp + line.raw[1]**2))/(self.grid_n/2), 1))**2.0
                        
        gamma = 1.0
        
        nx, ny = pathfind(self.grid, self.entity.raw, self.player.raw, self.stack, self.grid.shape[1], self.grid.shape[0])
        if nx >= 0 and ny >= 0:
            nv = Vec((nx, ny))
            self.entity -= ((self.entity - nv) * self.entity_step)
            
        s = time.perf_counter()
        for px in range(self.width):
            rot = self.view @ self.angles[px]
            res = raycast(cast(Vec, rot).raw, self.grid, self.player.raw, self.render_dist, self.sub_steps, self.grid_n, self.level, self.mask, self.scale)
            horiz += "1" if res[0] else "0"
            dist.append(res[1])
        rend = time.perf_counter()-s
        
        columns = np.zeros((self.width, 9))
        
        half = self.horizon_fac
        self.wob_ema = self.wob_ema * self.wob_ema_fac + self.wobble * math.sin((time.time() * self.wob_fac) % (2 * math.pi)) * self.move_ema * (1-self.wob_ema_fac)
        half+=self.wob_ema
        
        half*=self.height
        
        s = time.perf_counter()
        
        if self.flash:
            gamma = 2.0
            self.flash = False
            
        if (time.time()-self.since_pocket) > self.pocket_every and (self.pocket_n + 1 < self.p_notes) and self.level!=4:
            if horiz[self.width//2] == "1":
                target = self.player + (cast(Vec, (self.view @ Vec((1, 0)))) * (max(dist[self.width//2], 1/self.render_dist)*self.render_dist))
            else:
                target = self.player + (cast(Vec, self.view @ Vec((1, 0))) * (0.2*self.render_dist))
            
            self.grid[round(target.raw[1])][round(target.raw[0])] = 3
            self.mask[int(target.raw[1]//self.scale)][int(target.raw[0]//self.scale)] = 1
            
            if self.pocket.raw[0]>0 and self.pocket.raw[1]>0:
                self.grid[round(self.pocket.raw[1])][round(self.pocket.raw[0])] = 0
                
            self.pocket = target
            self.pocket_n+=1
            self.since_pocket = time.time()
            print("\a", end="", flush=True)
        
        if (time.time()-(self.since_rift))>=self.rift_time and not self.escape and not (self.level==4):
            if horiz[self.width//2] == "1":
                target = self.player + ((self.view @ Vec((1, 0))) * (dist[self.width//2]*self.render_dist))
                
                if self.grid[round(target.raw[1])][round(target.raw[0])] == 1:
                    self.grid[round(target.raw[1])][round(target.raw[0])] = 2
                    self.mask[int(target.raw[1]//self.scale)][int(target.raw[0]//self.scale)] = 1
                    self.rift = target

                    self.entity_step/=1.5
                    self.escape = True

                    gamma = 10.0
                    self.flash = True
                    print("\a", end="", flush=True)
        
        for px, (hit, p_dist) in enumerate(zip(horiz, dist)):
            if hit == "1" and p_dist >= 0:
                p_dist *= self.angles[px].raw[0]

            wh = int((self.wall_proj * self.height) / max(p_dist * self.render_dist, 0.25))
            top = half - (wh // 2)
            bottom = half + (wh // 2)
        
            ray_dir = cast(Vec, self.view @ self.angles[px])
            ray_depth = max(0.0, (dist[px] * self.render_dist) - 1.0)
            hit_pos = self.player + ray_dir * ray_depth
            
            x, y = round(hit_pos.raw[0]), round(hit_pos.raw[1])
            if self.lm is not None and 0<=y<self.grid_n and 0<=x<self.grid_n:
                light = self.lm[y][x] * (1-p_dist)
            else:
                light = 1.0

            eff = (max(0.0, 1-p_dist)**2.0) * self.global_shade * grad * max(self.ambient, light)
            eff = round(eff / self.quantise)*self.quantise
            
            wall = (min(round(self.theme.wall[0] * eff), 255), min(round(self.theme.wall[1] * eff), 255), min(round(self.theme.wall[2] * eff), 255))
            
            ray_dist = self.render_dist/max(self.angles[px].raw[0], 1e-5)
            columns[px] = ((float(hit == "1"), top, bottom, wall[0], wall[1], wall[2], ray_dir.raw[0], ray_dir.raw[1], ray_dist))

        if self.since_js<0 and not self.js:
            center = self.width // 2
            if time.time() >= self.next_js and self.level != 4:
                if horiz[center - 1] == "0" and horiz[center + 1] == "0":
                    self.since_js = time.time()
                    self.js = True
        if self.js:
            if (time.time()-self.since_js)>(self.js_time + 0.3*(1-grad)):
                self.js = False
                self.since_js = -1.0
                self.next_js = time.time()+random.random()*self.js_jitter*2 + (self.js_every-self.js_jitter)
        
        pool = self.glyphs if grad>=0.25 else self.death_glyphs
        get_glpyh = (lambda _: random.choice(pool)) if len(self.glyphs)>1 else (lambda _: self.glyphs[0])
        
        inst = max(0.0, (1-(time.time()-self.since_rift)/self.rift_time), 0.0)
        
        ct = time.time()
        
        out = raster(ct, columns, self.theme.floor, self.theme.roof, half, self.wall_proj, self.player.raw, self.grid_n, self.lm, gamma, self.quantise, self.in_water, self.wet_wall, self.ao, self.water_shine, self.wave_shade, self.wave_freq, self.wave_speed, self.move_ema, self.global_shade, grad, self.js, self.width, self.height, self.render_dist, self.ambient)
        
        tb = 0.0
        
        screen = []
        flat = out.reshape(-1, 3)
        prev = np.empty_like(flat)
        
        prev[0] = [-1,-1,-1]
        prev[1:] = flat[:-1]
        change = np.any(flat != prev, axis=1)
        change[0] = True
        
        flat = flat.reshape(self.height, self.width, 3)
        change = change.reshape(self.height, self.width)
        
        for iy in range(self.height):
            row = flat[iy]
            chg_row = change[iy]
            
            screen.append("".join(get_ansi(r, g, b, get_glpyh(0)) if chg else get_glpyh(0) for (r, g, b), chg in zip(row, chg_row)))
            
        buffer = "\n".join(screen)
        
        shade = time.perf_counter()-s
        
        print("\033[H" + col(buffer, 0, 0, 0, block=True), end="", flush=True)
        
        f_col = f"Fear: {round((1-grad)*100)}%"
        s_col = f"Stability: {round(inst*100)- (0 if self.level!=4 else 150)}%"
        msg = f"WASD to walk, O/P to turn, 1/2/3/4 to select graphics quality, T to toggle Pixel Preset (current: {'Block Grain' if self.mac else 'No Grain'}), and X to accept defeat | FPS: {self.fps} | {rend*1000.0:.2f}ms Render time | {shade*1000.0:.2f}ms Shade time | {f_col} | {s_col} | "
        print(f"\r\033[{self.height-1};1H{''.join(['_' for _ in range(len(msg)-1)])} ", end="", flush=True)
        
        msg = msg.replace(f_col, col(f"Fear: {round((1-grad)*100)}%", 255 if (1-grad>=0.3) else 0, 255 if (1-grad<0.6) else 0, 0))
        msg = msg.replace(s_col, col(f"Stability: {round(inst*100)- (0 if self.level!=4 else 100)}%", 255 if (inst<0.7 or self.level==4) else 0, 0 if (inst<0.3 or self.level==4) else 255, 0))
        print(f"\r\033[{self.height};1H{msg}", end="", flush=True)
        
state = State(24)
target = 1 / 30.0
since_resize = 0
since30 = time.perf_counter()
frames = 0
try:
    state.term.hide()
    while True:
        if since_resize >= 100:
            since_resize = 0
            state.resize()
        else:
            since_resize+=1
            
        s = time.perf_counter()
        state.update()
        state.render()
        
        elap = time.perf_counter() - s
        time.sleep(max(0.0, target - elap))
        frame_time = time.perf_counter() - s
        
        frames+=1
        if frames>=30:
            state.fps = round(30.0/(time.perf_counter()-since30))
            frames = 0
            since30 = time.perf_counter()
    
finally:
    state.term.show()
    
 # you sir, are a fish