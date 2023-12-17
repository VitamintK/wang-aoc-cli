# ask gpt or chatgpt to parse out the example
# tell it that we are doing Advent of Code.
# Give it a few few-shot examples
# Give it the real input
# Give it the html of the problem text.
# Ask it for the example input.

# WIP
from pathlib import Path

from openai import OpenAI

# FILE_EXTENSIONS = ['in', 'out', 'real', 'answer']
EXAMPLES = ['example_1', 'example_2', 'example_3']


def go(openai_key, puzzle_description: str, real_input: str, truncate_real = True):
    N = 10
    client = OpenAI(
        api_key=openai_key, 
    )
    ins = []
    outs = []
    for example in EXAMPLES:
        inp = open(Path(__file__).parent / f'{example}.in').read()
        real = open(Path(__file__).parent / f'{example}.real').read()
        if truncate_real:
            first_m = real[:1250]
            if len(real) >= 1250:
                first_m += ' ...'
            real = '\n'.join(real.split('\n')[:N])
        answer = open(Path(__file__).parent / f'{example}.answer').read()
        out = open(Path(__file__).parent / f'{example}.out').read()
        ins.append(f'Puzzle Description:\n{inp}\n\nReal Input:\n{real}')
        outs.append(f'{{"Example Input": "{out}", "Example Answer":"{answer}"}}')

    ins.append(f'Puzzle Description:\n{puzzle_description}\n\nReal Input:\n{real_input}')

    real_input_description= "Real Input" if truncate_real else f"(possibly truncated) Real Input",
    response = client.chat.completions.create(
        model="gpt-4-1106-preview", #"gpt-3.5-turbo",
        response_format={ "type": "json_object" },
        messages=[
                {"role": "system", "content": f"You are an expert parser of Advent of Code puzzles. The user will give you the body of an Advent of Code puzzle description, which contains an Example Input. \
                 You must return only the Example Input. To help, you will also be given the {real_input_description}, which may be much longer. There may be multiple inputs in the body, but the Example Input is the one that has an Example Answer.\
                 Rarely, there may be multiple Example Inputs. In that case, return the first one. Return the Example Input and the Example Answer as a JSON object."},
                {"role": "user", "content": f"{ins[0]}"},
                {"role": "assistant", "content": f"{outs[0]}"},
                {"role": "user", "content": f"{ins[1]}"},
                {"role": "assistant", "content": f"{outs[1]}"},
                {"role": "user", "content": f"{ins[2]}"},
                {"role": "assistant", "content": f"{outs[2]}"},
                {"role": "user", "content": f"{ins[3]}"}
            ]
    )
    return response.choices[0].message.content