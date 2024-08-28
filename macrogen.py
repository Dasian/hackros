# place curly braces around each character in a string so the streamdeck
# supermacro extension can paste text into a virtual machine

# the normal pasting functionality doesn't work since the keyboard isn't
# used as a hid device? something to do with pasting in a window?
# plus virtual machines input things weird so i'm using the super
# macro action to simulate real keypresses as opposed to just pasting
# a predefined string

import argparse
import os
import tkinter as tk

def main():
    parser = argparse.ArgumentParser(prog='macrogen',
                                     description='Converts input into the SuperMacro format for the Stream Deck')
    parser.add_argument('text', help='text to be converted into a macro', nargs='?', default=None)
    parser.add_argument('--loop', help='continue asking for user input', action='store_true')
    parser.add_argument('--inputfile', help='file with text to be converted')
    parser.add_argument('--gui', help='gui interface for setting the attacker and victim ip, will update related macros', action='store_true')
    parser.add_argument('--output', help='save output to a file')
    args = parser.parse_args()

    if args.gui:
        convert_gui()
    elif args.loop:
        # continuous conversion loop
        input_msg = 'Enter the string, hoe (or exit): '
        s = input(input_msg)
        while s != 'exit':
            print(convert(s))
            s = input(input_msg)
    elif args.text and type(args.text) == str:
        # convert from commandline str
        macro_str = convert(args.text) 
    elif args.inputfile and os.path.isfile(args.inputfile):
        # convert from file
        with open(args.inputfile) as f:
            lines = f.readlines()
            lines = [l.replace('\n', '') for l in lines]
            macro_str = '\n'.join(lines)
        macro_str = convert(macro_str) 
    else:
        parser.print_usage()
        return

    if args.output:
        # save to file
        with open(args.output, 'w') as f:
            f.write(macro_str)
    else:
        # output converted macro
        print(macro_str)
    return

# TODO improve gui
#   use a dict to replace keywords
# graphic user interface for inputting values
def convert_gui():
    frame = tk.Tk()
    frame.title('set ips')
    frame.geometry('300x250')

    # replace['variable_name'] = value
    replace = {}

    # victim
    victim_box = tk.Text(frame, height=2, width=20)
    victim_box.pack()
    def set_victim():
        print('set victim')
        inp = victim_box.get(1.0, 'end-1c')
        print(inp)
        fill_templates('victim', ip=inp)
    victim_submit = tk.Button(frame, text='victim ip', command=set_victim)
    victim_submit.pack()

    # attacker
    attacker_box = tk.Text(frame, height=2, width=20)
    attacker_box.pack()
    def set_attacker():
        print('set attacker')
        inp = attacker_box.get(1.0, 'end-1c')
        print(inp)
        fill_templates('attacker', ip=inp)
    attacker_submit = tk.Button(frame, text='attacker ip', command=set_attacker)
    attacker_submit.pack()

    # box name, also does other
    lab_name_box = tk.Text(frame, height=2, width=20)
    lab_name_box.pack()
    def set_lab_name():
        print('lab name')
        inp = lab_name_box.get(1.0, 'end-1c')
        print(inp)
        fill_templates('other', lab_name=inp)
    lab_name_submit = tk.Button(frame, text='lab name', command=set_lab_name)
    lab_name_submit.pack()

    # victim_domain
    domain_box = tk.Text(frame, height=2, width=20)
    domain_box.pack()
    def set_domain():
        print('set domain')
        inp = domain_box.get(1.0, 'end-1c')
        print(inp)
        fill_templates('victim-domain', domain=inp)
    domain_submit = tk.Button(frame, text='victim domain', command=set_domain)
    domain_submit.pack()

    frame.mainloop()
    return

# TODO rework directory structure
#   work on linux
# replace variables like VICTIM_IP from the macro templates
def fill_templates(directory, ip=None, domain=None, lab_name=None):
    # valid template variables
    target = None
    if directory == 'victim':
        target = 'VICTIM_IP'
    elif directory == 'attacker':
        target = 'ATTACKER_IP'
    elif directory == 'victim-domain':
        target = 'VICTIM_DOMAIN'
    elif directory == 'other':
        target = 'LAB_NAME'

    # get absolute file paths
    target_dir = 'templates\\'+directory
    template_paths = []
    template_fnames = []
    for f in os.listdir(target_dir):
        abs_path = os.getcwd() + '\\' + target_dir + '\\' +  f
        template_paths.append(abs_path)
        template_fnames.append(f)

    # fill templates
    macro_dir = 'macros\\'
    for i in range(len(template_fnames)):
        # read template + preprocess
        path = template_paths[i]
        f = open(path)
        lines = f.readlines()
        lines = [l.replace('\n', '') for l in lines]
        macro_str = '\n'.join(lines)
        f.close()

        # maybe if TARGET in macro_str
        # issues are updating only one value
        # and an update dict would update all macros
        # at the same time

        # replace target variable
        # convert to macro keystroke
        if ip is not None:
            macro_str = convert(macro_str.replace(target, ip)) 
        elif domain is not None:
            macro_str = convert(macro_str.replace(target, domain)) 
        elif lab_name is not None:
            macro_str = convert(macro_str.replace(target, lab_name))
        else:
            macro_str = convert(macro_str)

        # write updated macro
        print('updating', macro_dir +'\\'+template_fnames[i])
        f = open(macro_dir+'\\'+template_fnames[i], 'w')
        f.write(macro_str)
        f.close()

    return

# generate keystrokes from macro template
def convert(s):
    key_map = {' ': 'SPACE', '\n': 'RETURN', ',': 'OEM_COMMA', '=': 'OEM_PLUS', '.': 'OEM_PERIOD', '-': 'OEM_MINUS',
                ';': 'OEM_1', '/': 'OEM_2', '`': 'OEM_3', '[': 'OEM_4', '\\': 'OEM_5', ']': 'OEM_6', '\'': 'OEM_7'}
    shift_map = {'!': '1', '@': '2', '#': '3', '$': '4', '%': '5', '^': '6', '&': '7', '*': '8', '(': '9', ')': '0',
                 '<': 'OEM_COMMA', '+': 'OEM_PLUS', '>': 'OEM_PERIOD', '_': 'OEM_MINUS',
                 ':': 'OEM_1', '?': 'OEM_2', '~': 'OEM_3', '{': 'OEM_4', '|': 'OEM_5', '}': 'OEM_6', '"': 'OEM_7'}
    shift_prefix = '}{{SHIFT}{'
    shift_suffix = '}}{'
    s1 = '{'
    ignore = False
    for i in range(len(s)):
        c = s[i]

        # TODO make exception code cleaner
        # manual exception for double curly braces
        # keep characters in double braces untouched
        # maybe make an exception flag?
        # useful for shortcuts that don't exist in text
        # {{ALT}{ENTER}} {{CTRL}{z}}
        if c == '{' and i+1<len(s) and s[i+1] == '{':
            ignore = True
            if i > 0:
                s1 += '}{'
            continue
        elif ignore and c == '}' and s[i-1] == '}':
            ignore = False
            s1 += '}{'
            continue
        elif ignore:
            s1 += c
            continue

        # make every character it's own keystroke (fixes duplicates and some delay issues)
        # should also set the delay to maybe 30 ms in the streamdeck
        # there are redundant empty braces added, i do not care
        s1 += '}{'
        
        # shift shit
        if c.isupper():
            s1 += shift_prefix + c.lower() + shift_suffix
        elif c in shift_map.keys():
            c = shift_map[c]
            s1 += shift_prefix + c + shift_suffix
        
        # normal shit
        else:
            if c in key_map.keys():
                c = key_map[c]
            s1 += '{' + c + '}'
    s1 += '}'

    # TODO don't have,, empty braces to clean in the first place
    # remove empty curly braces
    while s1.find('{}') > -1:
        s1 = s1.replace('{}','')
    return s1

if __name__ == '__main__':
    main()
