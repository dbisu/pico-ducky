# License : GPLv2.0
# Copyright (c) 2021  Dave Bailey
# Authors: Dave Bailey (dbisu, @daveisu), Diego Contreras (@Desperationis)


import usb_hid
from adafruit_hid.keyboard import Keyboard

# comment out these lines for non_US keyboards
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS as KeyboardLayout
from adafruit_hid.keycode import Keycode

# uncomment these lines for non_US keyboards
# replace LANG with appropriate language
#from keyboard_layout_win_LANG import KeyboardLayout
#from keycode_win_LANG import Keycode

import supervisor

import time
import digitalio
from digitalio import DigitalInOut, Pull
from adafruit_debouncer import Debouncer
from board import *
import pwmio
import asyncio
import gc

supervisor.disable_autoreload()

class DuckyKeyboard:
    kbd = Keyboard(usb_hid.devices)
    layout = KeyboardLayout(kbd)

    @staticmethod
    def send_string(string):
        DuckyKeyboard.layout.write(string)

    @staticmethod 
    def press_key_combo(keys):
        for k in keys:
            DuckyKeyboard.kbd.press(k)
        DuckyKeyboard.kbd.release_all()

    @staticmethod
    def press_key(key):
        DuckyKeyboard.press_key_combo([key,])


class Pico:
    """ Wrapper to interact with Raspberry Pi Pico's board """
    led = pwmio.PWMOut(LED, frequency=5000, duty_cycle=0)

    @staticmethod 
    async def led_pwm_up():
        for i in range(100):
            if i < 50:
                Pico.led.duty_cycle = int(i * 2 * 65535 / 100)  # Up
            #time.sleep(0.01)
            await asyncio.sleep(0.01)

    @staticmethod 
    async def led_pwm_down():
        for i in range(100):
            if i >= 50:
                Pico.led.duty_cycle = 65535 - int((i - 50) * 2 * 65535 / 100)  # Down
            #time.sleep(0.01)
            await asyncio.sleep(0.01)

    @staticmethod
    async def blink_pico_led():
        """ Task to continiously blink board LED """
        led_state = False

        while True:
            if led_state:
                print("Turning LED on")
                await Pico.led_pwm_up()
                led_state = False
            else:
                print("Turning LED off")
                await Pico.led_pwm_down()
                led_state = True

            await asyncio.sleep(0)

    @staticmethod 
    def in_setup_mode() -> bool:
        setup_pin = digitalio.DigitalInOut(GP0)
        setup_pin.switch_to_input(pull=digitalio.Pull.UP)

        # Pull UP is default true so invert it
        return not setup_pin.value

# Language-specific commands that do something other than press a key.
DUCKY_COMMANDS = [
        "REM",
        "DELAY",
        "STRING",
        "STRINGLN",
        "DEFINE", # Language-Specific
        "VAR",
        "IF", # Program-Flow
        "ELSE",
        "END_IF",
        "WHILE",
        "END_WHILE",
        "FUNCTION",
        "END_FUNCTION",
        "RETURN",
]

# Commands that injects a keycode to the target
DUCKY_KEYS = {
    'WINDOWS': Keycode.WINDOWS, 'GUI': Keycode.GUI,
    'APP': Keycode.APPLICATION, 'MENU': Keycode.APPLICATION, 'SHIFT': Keycode.SHIFT,
    'ALT': Keycode.ALT, 'CONTROL': Keycode.CONTROL, 'CTRL': Keycode.CONTROL,
    'DOWNARROW': Keycode.DOWN_ARROW, 'DOWN': Keycode.DOWN_ARROW, 'LEFTARROW': Keycode.LEFT_ARROW,
    'LEFT': Keycode.LEFT_ARROW, 'RIGHTARROW': Keycode.RIGHT_ARROW, 'RIGHT': Keycode.RIGHT_ARROW,
    'UPARROW': Keycode.UP_ARROW, 'UP': Keycode.UP_ARROW, 'BREAK': Keycode.PAUSE,
    'PAUSE': Keycode.PAUSE, 'CAPSLOCK': Keycode.CAPS_LOCK, 'DELETE': Keycode.DELETE,
    'END': Keycode.END, 'ESC': Keycode.ESCAPE, 'ESCAPE': Keycode.ESCAPE, 'HOME': Keycode.HOME,
    'INSERT': Keycode.INSERT, 'NUMLOCK': Keycode.KEYPAD_NUMLOCK, 'PAGEUP': Keycode.PAGE_UP,
    'PAGEDOWN': Keycode.PAGE_DOWN, 'PRINTSCREEN': Keycode.PRINT_SCREEN, 'ENTER': Keycode.ENTER,
    'SCROLLLOCK': Keycode.SCROLL_LOCK, 'SPACE': Keycode.SPACE, 'TAB': Keycode.TAB,
    'BACKSPACE': Keycode.BACKSPACE,
    'A': Keycode.A, 'B': Keycode.B, 'C': Keycode.C, 'D': Keycode.D, 'E': Keycode.E,
    'F': Keycode.F, 'G': Keycode.G, 'H': Keycode.H, 'I': Keycode.I, 'J': Keycode.J,
    'K': Keycode.K, 'L': Keycode.L, 'M': Keycode.M, 'N': Keycode.N, 'O': Keycode.O,
    'P': Keycode.P, 'Q': Keycode.Q, 'R': Keycode.R, 'S': Keycode.S, 'T': Keycode.T,
    'U': Keycode.U, 'V': Keycode.V, 'W': Keycode.W, 'X': Keycode.X, 'Y': Keycode.Y,
    'Z': Keycode.Z, 'F1': Keycode.F1, 'F2': Keycode.F2, 'F3': Keycode.F3,
    'F4': Keycode.F4, 'F5': Keycode.F5, 'F6': Keycode.F6, 'F7': Keycode.F7,
    'F8': Keycode.F8, 'F9': Keycode.F9, 'F10': Keycode.F10, 'F11': Keycode.F11,
    'F12': Keycode.F12,

}




class DuckyInteger():
    """ Wrapper for all integers in DuckyScript 3.0 """
    def __init__(self, token : str):
        if not self.isint(token):
            raise Exception("{0} is not a valid integer.".format(token))

        self.integer = int(token)
        self.wrap()

    def get(self):
        self.wrap()
        return self.integer

    def wrap(self):
        self.integer = self.integer % 65536

    def __int__(self):
        self.wrap()
        return self.integer

    def __str__(self):
        self.wrap()
        return str(self.integer)

    @staticmethod
    def isint(token):
        return token.isdigit()

class DuckyBoolean(DuckyInteger):
    """ Wrapper for all booleans in DuckyScript 3.0.
        They are secretly DuckyIntegers for easier logic comparisons."""

    def __init__(self, token : str):
        if not self.isbool(token):
            raise Exception("{0} is not a valid boolean.".format(token))

        # In DuckyScript, all booleans are integers. 
        if token == "TRUE":
            super().__init__("1")

        if token == "FALSE":
            super().__init__("0")

    @staticmethod
    def isbool(token):
        return token == "TRUE" or token == "FALSE"

    def __str__(self):
        if self.integer == 0:
            return "FALSE"

        return "TRUE"


class DuckyScript():
    """ Wrapper to easily manipulate the file cursor when reading the script. """

    def __init__(self, path):
        file = open(path, "r")
        self.script = file.readlines()
        file.close()
        self.cursorpos = 0
    
    def length(self) -> int:
        return len(self.script)

    def get_position(self) -> int:
        return self.cursorpos

    def get_line(self):
        """ Returns the current line the cursor is reading. None if EOF. """

        if self.is_eof():
            return None

        return self.script[self.cursorpos]

    def is_eof(self) -> bool:
        # EOF is reached on the the line after the last line of the script.
        return self.cursorpos >= self.length()

    def seekl(self, line):
        """ Moves cursor to a certain line number, starting from 0. """

        self.cursorpos = max(min(line, self.length()), 0)

    def scroll(self):
        """ Scrolls cursor to the next line. Does not return anything. """

        self.seekl(self.cursorpos + 1)


class DuckyScope():
    """ Wrapper to declare what a "scope" in DuckyScript starts and ends with. """
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def is_start(self, command):
        return command == self.start

    def is_end(self, command):
        return command == self.end

class DuckyScopeAnalyzer():
    scopes = [ 
        DuckyScope("IF", "END_IF"), 
        DuckyScope("WHILE", "END_WHILE"), 
        DuckyScope("FUNCTION", "END_FUNCTION") 
    ]

    """ "Eats" tokens and analyses what the "net" scope of the current token is. """
    def __init__(self):
        self.scope = 0

    def eat(self, tokens):
        for scope in DuckyScopeAnalyzer.scopes:
            if scope.is_start(tokens[0]):
                self.scope += 1
                break

            elif scope.is_end(tokens[0]):
                self.scope -= 1
                break

    def get_scope(self):
        return self.scope



class DuckyParser():
    """ Analyses / verifies syntax and splits up text into tokens. """

    def __init__(self):
        pass

    def parse(self, line):
        if len(line.strip()) == 0:
            return []

        raw_tokens = self.basic_tokenize(line)

        command = raw_tokens[0]
        
        if command.startswith("$"):
            command = "VAR"
            raw_tokens.insert(0, command)

        if command not in DUCKY_COMMANDS and command not in DUCKY_KEYS and not command.endswith("()"):
            raise Exception("Invalid command {0} in {1}".format(command, raw_tokens))

        if command in ["STRING", "STRINGLN"]:
            return self.string_tokenize(line)

        if command == "VAR":
            var_name = raw_tokens[1]

            if not self.is_valid_variable(var_name):
                raise Exception("Invalid variable name {0}".format(var_name))

            if len(raw_tokens) < 3 or raw_tokens[2] != "=":
                raise Exception("No assignment operator.")

            return raw_tokens

        if command == "DEFINE":
            const_name = raw_tokens[1]
            if not self.is_valid_const(const_name):
                raise Exception("Invalid constant name {0}".format(const_name))

            return self.basic_tokenize(line, 2)

        if command == "DELAY":
            if len(raw_tokens) != 2:
                raise Exception("Invalid use of DELAY.")

            if not raw_tokens[-1].isdigit():
                raise Exception("Invalid delay length.")

            return raw_tokens

        if command in ["IF", "ELSE"]:
            if raw_tokens[-1] != "THEN":
                raise Exception("Missing THEN keyword in conditional statement.")

            if len(raw_tokens) < 3:
                raise Exception("Missing condition in conditional statement.")

            return raw_tokens

        if command == "WHILE":
            if len(raw_tokens) < 2:
                raise Exception ("Missing condition in conditional statement.")
            
            return raw_tokens

        if command == "FUNCTION":
            if len(raw_tokens) != 2:
                raise Exception ("Invalid function signature.")

            function_name = raw_tokens[1]

            if len(function_name.split("(")) != 2:
                raise Exception ("Missing () in function signature.")

            if not self.is_valid_const(function_name.strip("()")):
                raise Exception("Invalid function name.")

            return raw_tokens


        return raw_tokens

    def basic_tokenize(self, line, maxsplit=-1):
        line = line.strip()
        return line.split(" ", maxsplit)

    def string_tokenize(self, line):
        line = line.lstrip()
        line = line.rstrip("\n")
        return line.split(" ", 1)

    def is_valid_variable(self, var_name) -> bool:
        if not var_name.startswith("$"):
            return False;

        var_name = var_name.replace("$", "")
        var_name = var_name.replace("_", "")
        return self.is_alnum(var_name)

    def is_valid_const(self, const_name) -> bool:
        const_name = const_name.replace("_", "")
        return self.is_alnum(const_name)

    def is_alnum(self, string) -> bool:
        """ If a string is alphanumeric. Circuitpython 7.x doesn't implement
        this. """

        for char in string:
            if not char.isalpha() and not char.isdigit():
                return False
        return True


class DuckyFrame():
    """ Holds local data of a frame used by interpreter """
    def __init__(self, return_address):
        self.return_address = return_address # Line number in script

    def get_return(self):
        return self.return_address

class DuckyStack():
    """ Stack to hold stack frames """
    def __init__(self):
        self.stack = []

    def push(self, frame):
        self.stack.insert(0, frame)

    def pop(self):
        return self.stack.pop(0)

    def __len__(self):
        return len(self.stack)

class DuckyInterpreter():
    def __init__(self):
        # All variables are global as defined in DuckyScript 3.0
        # There is no scoping.
        self.variables = {} # { Name : Value }
        self.constants = {} # { Name : Value }
        self.functions = {} # { Name() : Line Number }

        self.parser = DuckyParser()
        self.stack = DuckyStack()

    def subtitute_tokens(self, tokens):
        """Subtitutes any variables, constants, or functions for their values.
        Also subtitutes TRUE to 1 and FALSE to 0."""
        if len(tokens) == 0:
            raise Exception("No tokens to substitute.")

        for i, token in enumerate(tokens):
            for var in self.variables:
                if var in token:
                    tokens[i] = token.replace(var, str(self.variables[var]))
                    token = tokens[i]

            for const in self.constants:
                if const in token:
                    tokens[i] = token.replace(const, str(self.constants[const]))
                    token = tokens[i]

            for function in self.functions:
                if function in token:
                    # DESIGN DECISION: Functions with no return value are falsy. 
                    return_value = self.run_function([function])
                    if return_value == None:
                        return_value = ["0",]
                   
                    return_value = self.subtitute_tokens(return_value) # May have another expression in it
                    return_value = " ".join(return_value)
                    tokens[i] = token.replace(function, return_value)
                    token = tokens[i]

            tokens[i] = token.replace("TRUE", "1")
            token = tokens[i]
            tokens[i] = token.replace("FALSE", "0")
            token = tokens[i]

        # After insertion of functions some tokens have spaces. Re-tokenize the
        # expression.
        tokens = " ".join(tokens)
        tokens = self.parser.basic_tokenize(tokens)

        return tokens



    def evaluate_expression(self, tokens):
        """ Evaluates math and logic expressions with eval(). Substitutes
        variables and constants, runs functions in an expression, FALSE to 0,
        and TRUE to 1. """

        if len(tokens) == 0:
            raise Exception("No expression to evaluate.")

        tokens = self.subtitute_tokens(tokens)
        
        for token in tokens:
            for char in token:
                if char not in "1234567890+-*/%^()x><!|&abcdefABCDEF=":
                    raise Exception("Not a valid arithmetic operation.")

        # Python has no && or || so use python equivalent
        expression = " ".join(tokens)
        expression = expression.replace("&&", "and")
        expression = expression.replace("||", "or")

        return eval(expression)

    def run_command(self, tokens):
        """ Run any DuckyScript commands that don't deal with control flow. """
        command = tokens[0]

        # TODO: refactor this code
        if command == "STRING":
            if len(tokens) == 1:
                raise Exception("There is no text after STRING")

            string = tokens[1]

            # As defined in DuckyScript 3.0, you can print out variables and
            # constants if and only if it is the only text to be printed.
            if string in self.constants:
                string = str(self.constants.get(string))
            elif string in self.variables:
                string = str(self.variables.get(string))

            DuckyKeyboard.send_string(string)

        if command == "STRINGLN":
            if len(tokens) == 1:
                raise Exception("There is no text after STRINGLN")

            string = tokens[1]
            # As defined in DuckyScript 3.0, you can print out variables and
            # constants if and only if it is the only text to be printed.
            if string in self.constants:
                string = str(self.constants.get(string))
            elif string in self.variables:
                string = str(self.variables.get(string))

            DuckyKeyboard.send_string(string)
            DuckyKeyboard.press_key(Keycode.ENTER)

        if command == "VAR":
            var_name = tokens[1]
            var_value = tokens[3:]

            if DuckyBoolean.isbool(var_value[0]):
                var_value = DuckyBoolean(var_value[0])

            else:
                var_value = int(self.evaluate_expression(var_value))
                var_value = DuckyInteger(str(var_value))

            self.variables[var_name] = var_value

        if command == "DEFINE":
            const_name = tokens[1]
            const_value = tokens[2]
            if const_name in self.constants:
                raise Exception("Runtime error: {0} is already defined.".format(const_name))
            self.constants[const_name] = const_value

        if command == "DELAY":
            length = int(tokens[1]) # In ms
            
            time.sleep(length / 1000.0)



        # If it is a key combination like CONTROL A, then run the entire line.
        if command in DUCKY_KEYS:
            keys = []

            # loop on each key - the filter removes empty values
            for key in filter(None, tokens):
                key = key.upper()
                # find the keycode for the command in the list
                command_keycode = DUCKY_KEYS.get(key, None)
                if command_keycode is not None:
                    # if it exists in the list, use it
                    keys.append(command_keycode)
                elif hasattr(Keycode, key):
                    # if it's in the Keycode module, use it (allows any valid keycode)
                    keys.append(getattr(Keycode, key))
                else:
                    # if it's not a known key name, show the error for diagnosis
                    raise Exception("Unknown key: {0}".format(key))
            
            DuckyKeyboard.press_key_combo(keys)


    def run_if(self, tokens):
        """ Recursive function to run if statements, even nested. """

        command = tokens[0]
        if command != "IF":
            return

        expression = tokens[1:-1] # IF ( CONDITION ) THEN
        result = self.evaluate_expression(expression)

        # Find the next valid ELSE IF
        if result == False:
            while result == False:
                tokens = self.skip_until(["ELSE", "END_IF"])
                if tokens[0] == "END_IF":
                    return None

                expression = tokens[2:-1] # ELSE IF ( CONDITION ) THEN
                result = self.evaluate_expression(expression)
                
                if result:
                    break

                self.script.scroll()

        # run_until runs the current line, so scroll 1 more line so that it
        # won't evaluate this IF again and crash.
        self.script.scroll() 

        # This is where the recursion happens. If there is another IF statement
        # inside this block, run_until will run it and call this function
        # again.
        tokens = self.run_until(["ELSE", "END_IF", "RETURN"])

        if tokens[0] == "RETURN":
            return tokens # Pass to function

        if tokens[0] == "ELSE":
            self.skip_until(["END_IF"])

        return None

    def save_function(self, tokens):
        """ Records address of function for later use. """
        function_name = tokens[1]
        if function_name in self.functions:
            raise Exception("Function {0} already defined.".format(function_name))

        self.functions[function_name] = self.script.get_position()
        self.skip_until(["END_FUNCTION"])

    def run_function(self, tokens):
        """ Run a function. Uses recursion and the stack to deal with nested
        functions. """

        command = tokens[0]
        if command not in self.functions:
            raise Exception("{0} is not a function".format(command))

        # Keep note of current execution and seek to function address
        address = self.functions[command]
        self.stack.push(self.script.get_position())
        self.script.seekl(address)
        self.script.scroll()

        # Run function
        ending_tokens = self.run_until(["END_FUNCTION", "RETURN"])
        self.script.seekl(self.stack.pop())

        if ending_tokens[0] == "RETURN" and len(ending_tokens) > 1:
            return ending_tokens[1:] # [1:] to deal with expressions in RETURN

        return None

    def run_while(self, tokens):
        command = tokens[0]
        if command != "WHILE":
            raise Exception("Not a WHILE loop.")

        expression = tokens[1:]
        return_address = self.script.get_position()
        result = self.evaluate_expression(expression.copy())

        while result == True:
            self.script.seekl(return_address)
            self.script.scroll()

            tokens = self.run_until(["END_WHILE", "RETURN"])

            if tokens[0] == "RETURN":
                return tokens

            result = self.evaluate_expression(expression.copy()) 

        return None



    def interpret(self, tokens):
        """ Interprets tokens in a global environment. Assumes clean syntax. """
        if len(tokens) == 0:
            return

        command = tokens[0]

        if command == "IF":
            return self.run_if(tokens)

        if command == "WHILE":
            return self.run_while(tokens)

        if command == "FUNCTION":
            self.save_function(tokens)
            return 

        if command.endswith("()"):
            if command in self.functions:
                return self.run_function(tokens)
            else:
                raise Exception("{0} is not defined.".format(command))



        self.run_command(tokens)

        return None


    def run_until(self, commands, run = True):
        """ Runs from current line to a command in the same scope that matches
        a command in `commands`. Returns matched line's tokens but doesn't run
        it. If matched line is the current line, it won't run.

        "Same Scope" is incredibly important for the recursive algorithm of
        handling nested control structures. Example:

        IF ( TRUE ) THEN <- run_until(["END_IF"])
            IF (TRUE) THEN
                STRING HELLO
            END_IF <- ignore

            IF (FALSE) THEN
                STRING WORLD
            END_IF <- ignore
        END_IF <- run_until ends here as it is the same scope"""

        scope_analyzer = DuckyScopeAnalyzer()
        line = self.script.get_line()
        tokens = self.parser.parse(line)
        pos = self.script.get_position()

        if tokens[0] in commands:
            return tokens

        while not self.script.is_eof():
            if run:
                result = self.interpret(tokens)
                if result != None and result[0] == "RETURN":
                    return result # Return statement caught

                # If script position changed, IF, WHEN, or FUNCTION ran and we
                # are at the END. Eat END so scope doesn't mess up.
                new_pos = self.script.get_position()
                if new_pos != pos:
                    new_line = self.script.get_line()
                    new_tokens = self.parser.parse(new_line)
                    scope_analyzer.eat(new_tokens)


            self.script.scroll()

            if self.script.is_eof(): 
                break

            line = self.script.get_line()
            tokens = self.parser.parse(line)
            pos = self.script.get_position()

            if len(tokens) == 0:
                continue

            # Only check for commands if non-empty
            if scope_analyzer.get_scope() <= 0 and tokens[0] in commands:
                return tokens

            # Has to be last in case command is a scope-identifier
            scope_analyzer.eat(tokens)

        return []

    def skip_until(self, commands):
        return self.run_until(commands, run=False)

    def run(self, script):
        self.script = script
        self.run_until([])



def run_script(path):
    interpreter = DuckyInterpreter()
    script = DuckyScript(path)
    # DEBUG: Get the whole backtrace by uncommenting these 
    # interpreter.run(script)
    # return

    try:
        interpreter.run(script)
    except Exception as e:
        current_line = script.get_position()
        print("ERROR Line {0}: {1}".format(current_line + 1, e))

time.sleep(0.5) # Wait for HID handshake to occur

if not Pico.in_setup_mode():
    print("Bytes free before script: {0}".format(gc.mem_free()))
    run_script("ducky.dd")
    print("Bytes free after script: {0}".format(gc.mem_free()))
else:
    print("Setup mode activated. Not running script.")


asyncio.run(Pico.blink_pico_led())

