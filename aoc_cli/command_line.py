import argparse
import os
import shutil
import json
import requests
import subprocess
from bs4 import BeautifulSoup

BASE_URL = 'https://adventofcode.com'
session = requests.Session()
session.headers.update({'User-Agent': 'kevinwang wang-aoc-cli https://github.com/VitamintK/wang-aoc-cli'})

# Get and set state in the config file ####
def get_config_path():
    config_dir = os.environ.get('XDG_CONFIG_HOME', os.path.join(os.path.expanduser('~'), '.config'))
    config_path = os.path.join(config_dir, 'aoc_cli', 'config.json')
    return config_path

def get_config_data():
    CONFIG_PATH = get_config_path()
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            data = json.load(f)
    else:
        data = {}
    return data

def write_config_data(data):
    CONFIG_PATH = get_config_path()
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(data, f)

def get_day_from_config():
    return get_config_data()['day']

def get_year_from_config_with_default():
    data = get_config_data()
    if 'year' in data:
        return data['year']
    else:
        return 2023
    
def get_token_from_config():
    data = get_config_data()
    if 'session_token' not in data:
        raise ValueError('You need to set your AOC session token. Use `aoc auth <session_token>`')
    return data['session_token']

def get_openai_key_from_config():
    data = get_config_data()
    if 'openai_key' not in data:
        raise ValueError('You need to set your OpenAI key. Use `aoc openai <openai_key>`')
    return data['openai_key']

# Get and save inputs from adventofcode.com ###
def get_real_input(year, day, token):
    url = f'{BASE_URL}/{year}/day/{day}/input'
    headers = {"Cookie": f"session={token}"}
    response = session.get(url, headers=headers, allow_redirects=False)
    response.raise_for_status()
    if 300 <= response.status_code < 400:
        # expired tokens 302 redirect to the overall leaderboard
        msg = f"the auth token ...{token[-4:]} is dead"
        raise ValueError(msg)
    return response.text

# common helper functions
def get_year_and_day_with_fallbacks(args):
    """For each of [year, date], use it if it's in args, otherwise check config, otherwise use a default."""
    day, year = args.day, args.year
    if day is None:
        day = get_day_from_config()
    if year is None:
        year = get_year_from_config_with_default()
    return year, day

def get_year_with_fallbacks(args):
    year = args.year
    if year is None:
        year = get_year_from_config_with_default()
    return year

def parse_html_and_get_articles(html):
    bs = BeautifulSoup(html, 'html.parser')
    articles = bs.find_all('article')
    assert len(articles) in [1, 2]
    # article.text looks really nice, but maybe preserving HTML tags helps find the example input more easily
    # use formatter=None so that < and > don't get escaped, although this means the result is not valid HTML
    # TODO: let the caller of this function decide whether to return article.text or article.decode_contents(formatter=None),
    #       maybe by just returning articles and letting the caller decode?
    return [article.decode_contents(formatter=None) for article in articles]

def run_python_with_input(py_path, input_path):
    output = []
    def execute(cmd, inp):
        popen = subprocess.Popen(cmd, stdin=inp, stdout=subprocess.PIPE, universal_newlines=True)
        for stdout_line in iter(popen.stdout.readline, ""):
            yield stdout_line 
        popen.stdout.close()
        # return_code = popen.wait()
        # if return_code:
        #     raise subprocess.CalledProcessError(return_code, cmd)
    with open(input_path, 'r') as input_file:
        for l in execute(['python', '-u', py_path], input_file):
            print(l, end="")
            output.append(l)
    return output

def submit_aux(year, day, level, answer):
    url = f'{BASE_URL}/{year}/day/{day}/answer'
    token = get_token_from_config()
    fields = {"level": level, "answer": answer}
    headers = {"Cookie": f"session={token}"}
    response = session.post(url, headers=headers, data=fields, allow_redirects=False)
    response.raise_for_status()
    if response.status_code != 200:
        print(f"got {response.status_code} status code")
        raise ValueError(f"HTTP {response.status_code} at {url}")
    articles = parse_html_and_get_articles(response.text)
    return articles[0]

###### commands ##############################################

def cd(args):
    # cd to /Users/kevin/AlgorithmProblems/miscellaneous/advent-of-code/2023
    # unfortunately, this is not possible. need to convert to a bash cmd to do this
    year = get_year_with_fallbacks(args)
    # print("run the following command:")
    # print("cd $(aoc cd)")
    print(f"cd ~/AlgorithmProblems/miscellaneous/advent-of-code/{year}")

def set_day(args):
    day = args.day
    data = get_config_data()
    data['day'] = day
    write_config_data(data)

def set_year(args):
    year = args.year
    data = get_config_data()
    data['year'] = year
    write_config_data(data)

def make(args):
    day = args.day
    if day is None:
        day = get_day_from_config()
    # copy the file 'boilerplate.py' to the file 'day{x}.py'
    py_path = f'day{day}.py'
    if os.path.exists(py_path):
        print(f'file {py_path} already exists. Not overwriting.')
    else:
        with open('boilerplate.py', 'r') as f:
            with open(py_path, 'w') as f2:
                shutil.copyfileobj(f, f2)

    example_in_filepath = f'day{day}_example.in'
    real_in_filepath = f'day{day}_real.in'
    for filepath in [example_in_filepath, real_in_filepath]:
        if os.path.exists(filepath):
            print(f'file {py_path} already exists. Not overwriting.')
        else:
            with open(filepath, 'w') as f:
                pass

def start_daemon():
    pass

def test(args):
    year, day = get_year_and_day_with_fallbacks(args)
    py_path = f'day{day}.py'
    if not os.path.exists(py_path):
        raise ValueError(f'file {py_path} does not exist. create it with `aoc make {day}`')
    example_in_filepath = f'day{day}_example.in'
    output = run_python_with_input(py_path, example_in_filepath)
    print(output, end='')
    
def submit(args):
    # used aocd/models.py:Puzzle._submit for inspiration
    # It has a lot of useful bells and whistles like tracking previous submissions which is really nice. also automatically fixing year,day if day,year is given.
    # so TODO: copy those nice features
    year, day = get_year_and_day_with_fallbacks(args)
    level = args.level
    answer = args.answer
    if level is None:
        level = 1
    if answer is None:
        answer = input('enter answer: ')
    answer = answer.strip()
    response = submit_aux(year, day, level, answer)
    print(response)

def run(args):
    level = args.level
    assert level is None or int(level) in [1,2]
    if level is None:
        print("level not specified. Setting level to 1")
        level = 1
    else:
        level = int(level)
    year, day = get_year_and_day_with_fallbacks(args)
    py_path = f'day{day}.py'
    if not os.path.exists(py_path):
        raise ValueError(f'file {py_path} does not exist. create it with `aoc make {day}`')
    real_in_filepath = f'day{day}_real.in'
    example_in_filepath = f'day{day}_example.in'
    example_answer_filepath = f'day{day}_example.answer'
    correct = False
    if os.path.exists(example_in_filepath):
        with open(example_in_filepath, 'r') as f:
            example_in = f.read()
        if example_in.strip() != '':
            print('Running on example:')
            output = run_python_with_input(py_path, example_in_filepath)
            example_ans = output[-1].strip()
            if os.path.exists(example_answer_filepath):
                with open(example_answer_filepath, 'r') as f:
                    expected_ans = f.read().strip()
                if example_ans == expected_ans:
                    print(f'Answer is correct: {example_ans}')
                    correct = True
                else:
                    print(f'Answer is incorrect: {example_ans}. Expected: {expected_ans}')
            print()
    print('Running on real input:')
    output = run_python_with_input(py_path, real_in_filepath)
    real_ans = output[-1].strip()
    print()
    if correct:
        print("The answer for the example input answer was correct.")
        print(f"The answer for the real input is: {real_ans}")
        go = input("Submit real answer? [Y/n] ") in ['Y', 'y', '']
    else:
        print("The example answer was incorrect or unknown. Submit anyways?")
        print(f"The answer for the real input is: {real_ans}")
        go = input("Submit real answer anyways? [y/N] ") in ['Y', 'y']
    if go:
        response = submit_aux(year, day, level, real_ans)
        print(response)
    else:
        print("Not submitting.")

def set_session_id(args):
    # TODO: add help message and error message telling you to do https://github.com/wimglenn/advent-of-code-wim/issues/1
    data = get_config_data()
    data['session_token'] = args.session_token
    write_config_data(data)

def set_openai_key(args):
    openai_key = args.openai_key
    if openai_key is None:
        openai_key = input('enter OpenAI key: ')
    data = get_config_data()
    data['openai_key'] = openai_key
    write_config_data(data)

def get_and_save_input(args):
    year, day = get_year_and_day_with_fallbacks(args)
    token = get_token_from_config()
    real_input = get_real_input(year, day, token)
    with open(f'day{day}_real.in', 'w') as f:
        f.write(real_input)

def get_and_save_description(args):
    year, day = get_year_and_day_with_fallbacks(args)
    token = get_token_from_config()
    url = f'{BASE_URL}/{year}/day/{day}'
    headers = {"Cookie": f"session={token}"}
    response = session.get(url, headers=headers, allow_redirects=False)
    response.raise_for_status()
    if response.status_code != 200:
        print(f"got {response.status_code} status code")
        raise ValueError(f"HTTP {response.status_code} at {url}")
    articles = parse_html_and_get_articles(response.text)
    with open(f'day{day}_description.html', 'w') as f:
        f.write(articles[0])

def get_real_and_description_and_parse_example(args):
    # get_and_save_description(args)
    # get_and_save_input(args)
    year, day = get_year_and_day_with_fallbacks(args)
    with open(f'day{day}_description.html', 'r') as f:
        html = f.read()
    with open(f'day{day}_real.in', 'r') as f:
        real_input = f.read()
    from aoc_cli.parse_example import parse_example
    parsed_example = json.loads(parse_example.go(get_openai_key_from_config(), html, real_input))
    print(parsed_example)
    with open(f'day{day}_example.in', 'w') as f:
        f.write(parsed_example['Example Input'])
    with open(f'day{day}_example.answer', 'w') as f:
        f.write(parsed_example['Example Answer'])

def debug(args):
    data = get_config_data()
    print(data)

################################################

def main():
    # create the top-level parser
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help')

    parser_cd = subparsers.add_parser('cd', help='This should cd you to the AOC directory. But it does not work :(', description="This does not work :(")
    parser_cd.add_argument('year', nargs='?', default=None)
    parser_cd.set_defaults(func = cd)

    parser_day = subparsers.add_parser('day', help='Set the current day, so that any subsequent commands know what day to operate on.')
    parser_day.add_argument('day', help='day help')
    parser_day.set_defaults(func = set_day)

    parser_year = subparsers.add_parser('year', help='Set the current year, so that any subsequent commands know what year to operate on.')
    parser_year.add_argument('year', help='year help')
    parser_year.set_defaults(func = set_year)

    parser_make = subparsers.add_parser('make', help='Creates the .py and .in files for a specific day.')
    parser_make.add_argument('day', nargs='?', default=None, help='day help')
    parser_make.set_defaults(func = make)

    parser_auth = subparsers.add_parser('auth', help='Sets auth token')
    parser_auth.add_argument('session_token', help='session_token help')
    parser_auth.set_defaults(func = set_session_id)

    parser_openai = subparsers.add_parser('openai', help='Set OpenAI API key')
    parser_openai.add_argument('openai_key', nargs='?', default=None, help='openai_key help')
    parser_openai.set_defaults(func = set_openai_key)

    parser_save_real = subparsers.add_parser('get-real', help='Download and save the real input for the day')
    parser_save_real.add_argument('year', nargs='?', default=None)
    parser_save_real.add_argument('day', nargs='?', default=None)
    parser_save_real.set_defaults(func = get_and_save_input)

    parser_get_description = subparsers.add_parser('get-description', help='Get the description of the puzzle for the day')
    parser_get_description.add_argument('year', nargs='?', default=None)
    parser_get_description.add_argument('day', nargs='?', default=None)
    parser_get_description.set_defaults(func = get_and_save_description)

    parser_parse_example = subparsers.add_parser('parse-example', help='Parse the example input from the description of the puzzle for the day')
    parser_parse_example.add_argument('year', nargs='?', default=None)
    parser_parse_example.add_argument('day', nargs='?', default=None)
    parser_parse_example.set_defaults(func = get_real_and_description_and_parse_example)

    parser_daemon = subparsers.add_parser('daemon', help="Start a daemon that checks if the day's puzzle is released and gets the inputs when it is.")
    parser_daemon.set_defaults(func = start_daemon)

    # run example only
    parser_test = subparsers.add_parser('test', help='test help')
    parser_test.add_argument('year', nargs='?', default=None)
    parser_test.add_argument('day', nargs='?', default=None)
    parser_test.set_defaults(func = test)

    # run both example and input (if available)
    parser_run = subparsers.add_parser('run', help='run help')
    parser_run.add_argument('level', nargs='?', default=None)
    parser_run.add_argument('year', nargs='?', default=None)
    parser_run.add_argument('day', nargs='?', default=None)
    parser_run.set_defaults(func = run)

    # submit
    parser_submit = subparsers.add_parser('submit', help='submit the answer: `aoc submit 1` to submit part 1 for the day')
    parser_submit.add_argument('level', nargs='?', default=None)
    parser_submit.add_argument('year', nargs='?', default=None)
    parser_submit.add_argument('day', nargs='?', default=None)
    parser_submit.add_argument('answer', nargs='?', default=None)
    parser_submit.set_defaults(func = submit)

    # debug
    parser_debug = subparsers.add_parser('debug')
    parser_debug.set_defaults(func = debug)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()