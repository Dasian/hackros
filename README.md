# Hackros
Converts strings into the [SuperMacro](https://docs.barraider.com/faqs/supermacro/getting-started/#)
format for use with the [Elgato Stream Deck](https://www.elgato.com/us/en/s/welcome-to-stream-deck).
Supports macro variables and is used to write commands in a kali linux virtual machine.

## Why??
The stream deck's default pasting functionality doesn't work correctly with virtual machines (the
machine usually crashes).
By simulating each key stroke we can "paste" into virtual machines using macros. Doing it this way
allows us to add variables into the macros which can be changed during generation! 

When playing a CTF on TryHackMe or HackTheBox there are often repetitve commands such as an nmap scan,
directory bruteforce, or stabilizing a reverse shell. By making macro templates with a macro variable
set to the IP or domain name of our target box, we can execute these commands with one button!

> [!NOTE]
> Since this repo's creation the [SuperMacro](https://docs.barraider.com/faqs/supermacro/variables/) plugin has been updated to include variables and the **pasting of text directly into a virtual machine with the "Forced Macro Mode" option. I'm still going to update this repo since I've included it in my workflow but check out the changes!

# Installation
> [!NOTE]
> The SuperMacro plugin and this script will only work on Windows

Clone the repository
```cmd
git clone https://github.com/Dasian/hackros.git
```

Install the required pacakages
```cmd
pip3 install -r requirements.txt
```

# Usage
Filing variables only works in the tui mode and will write the macros in the "generated_hackros" directory
```cmd
python hackros.py --tui
```

There are other command line options for smaller conversions
```
usage: hackros [-h] [--loop] [--inputfile INPUTFILE] [--tui] [--output OUTPUT] [text]

Converts input into the SuperMacro format for the Stream Deck

positional arguments:
  text                  text to be converted into a macro

options:
  -h, --help            show this help message and exit
  --loop                continue asking for user input
  --inputfile INPUTFILE
                        file with text to be converted
  --tui                 tui interface for setting the attacker and victim ip, will update related macros
  --output OUTPUT       save output to a file
```

# TODO
- [x] Improve cmdline
- [x] Create README
- [X] Replace GUI with TUI
- [ ] Rework filling variables
- [ ] Improve Frontend
- [ ] Implement Wildcard Command
- [ ] Add Credentials/Profiles
- [~] Clean code
