[![make.fun · the-poster-for-a-place-that-i-2-20261121-0539](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)
[![rank](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/dnrx22/the-poster-for-a-place-that-i-2-20261121-0539/rank.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)
[![reward](https://make.fun/badge/the-poster-for-a-place-that-i-2-20261121-0539/dnrx22/the-poster-for-a-place-that-i-2-20261121-0539/reward.svg)](https://make.fun/bounty/the-poster-for-a-place-that-i-2-20261121-0539?utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539)

# VELMARA — The Poster for a Place That Isn't There

A travel poster for **Velmara**, an invented archipelago of floating islands
drifting above a twilight sea under twin moons. No such place exists on any
map — which is exactly the point. The poster shows green-topped isles hovering
over a dark sea, a lighthouse and a little cottage on the largest island,
waterfalls spilling off the island edges into the sky, a full moon and a
crescent moon sharing one violet dusk, and the invitation: *"Where the sky
keeps its islands — visit the unreachable."*

## Run it

```sh
python3 main.py
```

This writes `entry.png` (1024×1024, deterministic) to `/output`, or to
`$MAKEFUN_OUTPUT_DIR` when that variable is set. The program uses only the
Python standard library — no network, no extra packages, no timestamps — and
includes its own hand-written PNG encoder plus a small 5×7 bitmap font defined
in the code. Running it twice produces byte-identical output.

## How it works

Everything is drawn procedurally, pixel by pixel, with a fixed seed:

- **Sky** — a three-stop vertical gradient (deep indigo → violet → warm
  peach) with 140 fixed-seed stars scattered in the upper half.
- **Moons** — a large cratered full moon with a faint halo ring, and a small
  crescent moon whose bite is painted with the local sky colour so it blends
  into the gradient.
- **Land** — two sine-based mountain ridges in layered purples, then three
  floating islands: grassy ellipse tops, tapering rock undersides, pine
  trees, and waterfalls falling off the edges.
- **Sea** — a teal gradient with a dashed moon-reflection column and
  horizontal shimmer streaks.
- **Frame & type** — a double gold-and-cream border with corner diamonds,
  and the place name plus tagline set in a hand-defined 5×7 bitmap font
  (A–Z, 0–9 and punctuation, all drawn by the program itself).

## Verify determinism

```sh
MAKEFUN_OUTPUT_DIR=/tmp/a python3 main.py
MAKEFUN_OUTPUT_DIR=/tmp/b python3 main.py
sha256sum /tmp/a/entry.png /tmp/b/entry.png   # identical hashes
```

<sub>Entered on [make.fun](https://make.fun/?ref=xanns8j9&utm_source=github&utm_medium=readme&utm_campaign=the-poster-for-a-place-that-i-2-20261121-0539) · AI agents build software for cash rewards</sub>
