# wang-aoc-cli
Kevin Wang's CLI tool for advent of code

There are already, uh, 143492 different cmdline tools for Advent of Code.  
See: https://github.com/Bogdanp/awesome-advent-of-code#tools-and-utilities

However, this one is unique in that I am making it.

Due to this, it is bespoke for the way I do AOC, e.g. using `.in` files to store inputs.

[wimglenn/advent-of-code-data](https://github.com/wimglenn/advent-of-code-wim) seems to be one of the most popular and polished tools, and I used it for inspiration and its approach and some code for authing to AOC ( https://github.com/wimglenn/advent-of-code-wim/issues/1 )

Installation:

- Clone the repo
- `cd` into the repo
- install with pip: `pip install .` or `pip install -e .` (the [latter](https://setuptools.pypa.io/en/latest/userguide/development_mode.html) lets you edit the tool without re-installing after every modification.)

Usage:

```
aoc day 12
aoc make
aoc daemon
```

This tells the tool that the day is 12,  
creates the `day12.py` and `day12_real.in` and `day12_example.in` files (with `day12.py` copied from boilerplate.py),  
and waits until midnight, at which point it (1) downloads the input and saves it to `day12_real.in`, (2) downloads the problem description and saves to `day12_description.html`, (3) attempts to parse the example input and expected answer from that html using ChatGPT, and saves those to `day12_example.in` and `day12_example.answer`.

Then,
```
aoc run
```
- runs `python day12.py < day12_example.in`
- checks the answer (assumed to be the last line of stdout) by comparing it to `day12_example.answer`
- runs `python day12.py < day12_real.in`
- prompts the user as to whether they want to submit the answer to aoc, defaulting to "yes" if the example answer was correct, and no otherwise.

Example:  
```
> aoc run
level not specified. Setting level to 1
Running on example:
62
Answer is correct: 62

Running on real input:
46334

The answer for the example input answer was correct.
The answer for the real input is: 46334
Submit real answer? [Y/n] y
<p>That's the right answer!  You are <span class="day-success">one gold star</span> closer to restoring snow operations. You achieved <em>rank 3</em> on <a href="/2023/leaderboard/day/18">this star's leaderboard</a> and gained <em>98 points</em>! <a href="/2023/day/18#part2">[Continue to Part Two]</a></p>
```

For part 2, you need to run `aoc run 2` so that the tool knows which part it's submitting to.