import argparse
import os
import shutil
import json
import requests
import subprocess

BASE_URL = 'https://adventofcode.com'

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
    response = requests.get(url, headers=headers, allow_redirects=False)
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

def parse_html_and_get_article(html):
    # TODO: copy aocd and make this nicer with beautifulsoup
    return html.split('article')[1]

def execute(cmd, inp):
    popen = subprocess.Popen(cmd, stdin=inp, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    # return_code = popen.wait()
    # if return_code:
    #     raise subprocess.CalledProcessError(return_code, cmd)
def run_python_with_input(py_path, input_path):
    with open(input_path, 'r') as input_file:
        for l in execute(['python', '-u', py_path], input_file):
            print(l, end="")

###### commands ##############################################

def cd(args):
    # cd to /Users/kevin/AlgorithmProblems/miscellaneous/advent-of-code/2023
    # unfortunately, this is not possible. need to convert to a bash cmd to do this
    pass

def set_day(args):
    day = args.day
    data = get_config_data()
    data['day'] = day
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
    url = f'{BASE_URL}/{year}/day/{day}/answer'
    token = get_token_from_config()
    fields = {"level": level, "answer": answer}
    headers = {"Cookie": f"session={token}"}
    response = requests.post(url, headers=headers, data=fields, allow_redirects=False)
    response.raise_for_status()
    if response.status_code != 200:
        print(f"got {response.status_code} status code")
        raise ValueError(f"HTTP {response.status_code} at {url}")
    print(parse_html_and_get_article(response.text))

def run(args):
    year, day = get_year_and_day_with_fallbacks(args)
    py_path = f'day{day}.py'
    if not os.path.exists(py_path):
        raise ValueError(f'file {py_path} does not exist. create it with `aoc make {day}`')
    real_in_filepath = f'day{day}_real.in'
    output = run_python_with_input(py_path, real_in_filepath)
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
    url = f'{BASE_URL}/{year}/day/{day}/answer'
    token = get_token_from_config()
    fields = {"level": level, "answer": answer}
    headers = {"Cookie": f"session={token}"}
    response = requests.post(url, headers=headers, data=fields, allow_redirects=False)
    response.raise_for_status()
    if response.status_code != 200:
        print(f"got {response.status_code} status code")
        raise ValueError(f"HTTP {response.status_code} at {url}")
    print(parse_html_and_get_article(response.text))

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

def debug(args):
    data = get_config_data()
    print(data)

################################################

def main():
    # create the top-level parser
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help')

    parser_cd = subparsers.add_parser('cd', help='This should cd you to the AOC directory. But it does not work :(', description="This does not work :(")
    parser_cd.set_defaults(func = cd)

    parser_day = subparsers.add_parser('day', help='Set the current day, so that any subsequent commands know what day to operate on.')
    parser_day.add_argument('day', help='day help')
    parser_day.set_defaults(func = set_day)

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

    parser_daemon = subparsers.add_parser('daemon', help="Start a daemon that checks if the day's puzzle is released and gets the inputs when it is.")
    parser_daemon.set_defaults(func = start_daemon)

    # only example
    parser_test = subparsers.add_parser('test', help='test help')
    parser_test.add_argument('year', nargs='?', default=None)
    parser_test.add_argument('day', nargs='?', default=None)
    parser_test.set_defaults(func = test)

    # both example and input (if available)
    parser_run = subparsers.add_parser('run', help='run help')
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