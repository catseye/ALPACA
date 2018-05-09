Making animated GIFs with ALPACA and kinoje
===========================================

_This document describes a functionality of which the ALPACA
reference implementation is capable, but is not a part of the
ALPACA specification._

The reference implementation of ALPACA can output one SVG file
for each generation of the cellular automaton it has been
instructed to evolve.

These SVG files can be rendered and combined with a tool like
[kinoje](https://github.com/catseye/kinoje) to produce an
animated GIF.

Create the directories to store intermediate files first:

    mkdir instants
    mkdir frames

Run ALPACA like:

    alpaca eg/life_initial2.alp \
        --display-window='(0,0)-(10,10)' \
        --display-svg \
        --write-discrete-files-to=instants/ \
        --generations 30

Create a kinoje config file `life.yaml` like:

    duration: 3.0
    fps: 10.0
    width: 20
    height: 20
    command: inkscape -z -e {outfile} -w {width} -h {height} {infile}

Then run kinoje commands

    kinoje-render life.yaml instants/ frames/
    kinoje-compile life.yaml frames/ life.gif
