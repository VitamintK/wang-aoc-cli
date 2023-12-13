# wang-aoc-cli
Kevin Wang's CLI tool for advent of code

There are already, uh, 143492 different cmdline tools for Advent of Code.  
See: https://github.com/Bogdanp/awesome-advent-of-code#tools-and-utilities

However, this one is unique in that I am making it.

Due to this, it is bespoke for the way I do AOC, e.g. using `.in` files to store inputs.

wimglenn/advent-of-code-data seems to be one of the most popular and polished tools, and I used its approach and some code for authing to AOC: https://github.com/wimglenn/advent-of-code-wim/issues/1 and other things.

Usage:

```
aoc day 12
aoc make
aoc get-real
```

This tells the tool that the day is 12,  
creates the day12.py and day12_real.in and day12_example.in files (with day12.py copied from boilerplate.py),  
and downloads the input and saves it to day12_example.in

Then,
```
aoc run
```
runs `python day12.py < day12_real.in`
