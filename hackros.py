# place curly braces around each character in a string so the streamdeck
# supermacro extension can paste text into a virtual machine

# fills predefined macro variables (VICTIM_IP, ATTACKER_IP, etc.)
# based on directory structure
# prevents regenerating macros but code is less clean

# creates an exception for templates with double braces
# in order to manually add shortcuts 
# {{ctrl}{c}} -> ctrl + c

# the normal pasting functionality doesn't work since the keyboard isn't
# used as a hid device? something to do with pasting in a window?
# plus virtual machines input things weird so i'm using the super
# macro action to simulate real keypresses as opposed to just pasting
# a predefined string

# *** they fixed default text input with the forced macro option ***
# there is also support for variables but not sure if it applies to all
# macros/would need to read from a file for each macro which is annoyin

import argparse
import platform
import os

def main():
    parser = argparse.ArgumentParser(prog='hackros',
                                     description='Converts input into the SuperMacro format for the Stream Deck')
    parser.add_argument('text', help='text to be converted into a macro', nargs='?', default=None)
    parser.add_argument('--loop', help='continue asking for user input', action='store_true')
    parser.add_argument('--inputfile', help='file with text to be converted')
    parser.add_argument('--tui', help='tui interface for setting the attacker and victim ip, will update related macros', action='store_true')
    parser.add_argument('--output', help='save output to a file')
    args = parser.parse_args()

    hackro = HackroGenerator()

    if args.tui:
        # text user interface pog
        tui(hackro)
        exit()
    elif args.loop:
        # continuous conversion loop
        input_msg = 'Enter the string, hoe (or exit): '
        s = input(input_msg)
        while s != 'exit':
            print(hackro.convert(s))
            s = input(input_msg)
    elif args.text and type(args.text) == str:
        # convert from commandline str
        macro_str = hackro.convert(args.text) 
    elif args.inputfile and os.path.isfile(args.inputfile):
        # convert from file
        with open(args.inputfile) as f:
            lines = f.readlines()
            lines = [l.replace('\n', '') for l in lines]
            macro_str = '\n'.join(lines)
        macro_str = hackro.convert(macro_str) 
    else:
        parser.print_usage()
        exit()

    if args.output:
        # save to file
        with open(args.output, 'w') as f:
            f.write(macro_str)
    elif macro_str != None:
        # output converted macro
        print(macro_str)
    return

# text user interface
def tui(hackro=None):
    if hackro is None:
        hackro = HackroGenerator()

    # replacement values found in templates
    hackro.tokens['ATTACKER_IP'] = '10.10.14.18'
    hackro.tokens['VICTIM_IP'] = '10.10.11.90'
    hackro.tokens['VICTIM_DOMAIN'] = 'box.htb'
    hackro.tokens['LAB_NAME'] = 'box'

    import tui
    app = tui.HackrosApp()
    app.run()

    return

class HackroGenerator():
    def __init__(self, tokens={}):
        # dictionary of values to replace + value to replace with
        # hackro.tokens['VICTIM_IP'] = '10.10.11.11'
        self.tokens = tokens
        self.tokens['USER'] = 'USER'
        self.tokens['PASSWORD'] = 'PASSWORD'

        # special characters
        self.key_map = {' ': 'SPACE', '\n': 'RETURN', ',': 'OEM_COMMA', '=': 'OEM_PLUS', '.': 'OEM_PERIOD', '-': 'OEM_MINUS',
                    ';': 'OEM_1', '/': 'OEM_2', '`': 'OEM_3', '[': 'OEM_4', '\\': 'OEM_5', ']': 'OEM_6', '\'': 'OEM_7'}

        # special chars that need a shift
        # ! = shift + 1
        self.shift_map = {'!': '1', '@': '2', '#': '3', '$': '4', '%': '5', '^': '6', '&': '7', '*': '8', '(': '9', ')': '0',
                     '<': 'OEM_COMMA', '+': 'OEM_PLUS', '>': 'OEM_PERIOD', '_': 'OEM_MINUS',
                     ':': 'OEM_1', '?': 'OEM_2', '~': 'OEM_3', '{': 'OEM_4', '|': 'OEM_5', '}': 'OEM_6', '"': 'OEM_7'}
        return

    def generate_all_hackros(self) -> None:
        for key in self.tokens.keys():
            self.fill_templates(key)

    # update hackros with the token string
    # 'ATTACKER_IP' generates 
    def generate_hackro(self, token: str) -> None:
        if token not in self.tokens.keys():
            raise(f'{token} does not exist! Valid tokens: {self.tokens.keys()}')
        self.fill_templates(token)
    
    # hack solution to generate the "other" templates
    def refresh_misc(self) -> None:
        self.tokens['other'] = ''
        self.fill_templates('other')

    # replace variables like VICTIM_IP from the macro templates
    # target: token to replace in template files
    def fill_templates(self, target: str) -> None:
        if platform.system() == 'Linux':
            file_delim = '/'
        else:
            file_delim = '\\'

        # get absolute file paths of templates for reading
        template_dir = f'{os.getcwd()}{file_delim}templates{file_delim}{target}'
        # absolute paths to template files
        template_paths = []
        # names of hackro files to generate
        hackro_fnames = []
        for f in os.listdir(template_dir):
            abs_path = f'{template_dir}{file_delim}{f}'
            template_paths.append(abs_path)
            hackro_fnames.append(f)
        
        # grab multiple token templates if target token exists
        template_dir = f'{os.getcwd()}{file_delim}templates{file_delim}multiple-tokens'
        mult_paths = []
        for f in os.listdir(template_dir):
            abs_path = f'{template_dir}{file_delim}{f}'
            with open(abs_path) as fcheck:
                if target in fcheck.read():
                    mult_paths.append(abs_path)
                    hackro_fnames.append(f)

        # create output directory for hackros
        hackro_dir = f'generated_hackros{file_delim}'
        if not os.path.isdir(hackro_dir):
            os.makedirs(hackro_dir)

        # fill templates, convert to keystroke format,
        # then write to file
        for i, path in enumerate(template_paths + mult_paths):
            # read template + place it into one string
            with open(path) as f:
                lines = f.readlines()
                lines = [l.replace('\n', '') for l in lines]
                macro_str = '\n'.join(lines)

            # replace target variable in template 
            if i < len(template_paths):
                # single token
                macro_str = macro_str.replace(target, self.tokens[target])
            else:
                # multiple tokens
                for key in self.tokens.keys():
                    if key in macro_str:
                        macro_str = macro_str.replace(key, self.tokens[key])

            # convert to macro keystroke
            macro_str = self.convert(macro_str) 

            # write updated macro
            hackro_path = f'{hackro_dir}{hackro_fnames[i]}'
            with open(hackro_path, 'w') as f:
                f.write(macro_str)
        return

    # generate keystrokes from macro template
    # str s: raw string to convert to keystroke format
    # returns the keystroke formatted string
    def convert(self, s: str) -> str:
        shift_prefix = '}{{SHIFT}{'
        shift_suffix = '}}{'

        # keystroke string we'll return
        s1 = '{'

        # start variable?
        ignore = False

        # convert each character to their keystroke counterpart
        # special cases for special characters (spaces, newlines, etc.)
        # and characters from shift combination (! = shift + 1)
        for i in range(len(s)):
            c = s[i]

            # TODO make exception code cleaner

            # manual exception for double curly braces
            # keep characters in double braces untouched
            # maybe make an exception flag?
            # useful for shortcuts that don't exist in text
            # {{ALT}{ENTER}} {{CTRL}{z}}
            if c == '{' and i+1<len(s) and s[i+1] == '{':
                # start characters {{ found, ignore inner brace
                ignore = True
                if i > 0:
                    s1 += '}{'
                continue
            elif ignore and c == '}' and s[i-1] == '}':
                # outer brace }} found, continue converting
                ignore = False
                s1 += '}{'
                continue
            elif ignore:
                # add ignored characters
                s1 += c
                continue

            # make every character it's own keystroke (fixes duplicates and some delay issues)
            # should also set the delay to maybe 30 ms in the streamdeck
            # there are redundant empty braces added, i do not care
            s1 += '}{'
            
            # character that require a shift
            if c.isupper():
                s1 += shift_prefix + c.lower() + shift_suffix
            elif c in self.shift_map.keys():
                c = self.shift_map[c]
                s1 += shift_prefix + c + shift_suffix
            
            # normal shit
            else:
                if c in self.key_map.keys():
                    c = self.key_map[c]
                s1 += '{' + c + '}'
        s1 += '}'

        # TODO don't have,, empty braces to clean in the first place
        # remove empty curly braces
        while s1.find('{}') > -1:
            s1 = s1.replace('{}','')
        return s1

if __name__ == '__main__':
    main()
