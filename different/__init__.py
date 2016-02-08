import curtsies.events
from curtsies import FullscreenWindow, Input, FSArray, fsarray, fmtstr
import curtsies.fmtfuncs # import red, bold, green, on_blue, yellow, on_red
import re

TAB = '\t'
CR = '\r'
NL = '\n'
SPACE = ' '
WHITESPACE = r'[ \t\r\n]+'

class Repl:
    def __init__(self):
        self.prompt = getattr(self, 'prompt', '')
        self.complete_on = getattr(self, 'complete_on', TAB)
        self.read_until = getattr(self, 'read_until', CR)
        self.highlight = getattr(self, 'highlight', [])
        self.history_file = getattr(self, 'history_file')
        self.history = getattr(self, 'history', [])
        self.intro = getattr(self, 'intro', '')

    def loop(self):
        if self.history_file:
            with open(self.history_file, 'a+') as f:
                f.seek(0)
                self.history = f.read().split('\n') + self.history
                self.new_history = len(self.history)

        self.wait_completion = False
        self.line = 0
        self.column = 0
        with FullscreenWindow() as window:
            with Input() as input_generator:
                self.a = FSArray(window.height, window.width)
                intro_lines = self.intro.split('\n')
                for i, line in enumerate(intro_lines):
                    self.write_xy(i, 0, line)
                self.write_xy(self.line + 1, 0, self.prompt)
                window.render_to_terminal(self.a) # intro and prompt

                text = ''
                begin_line = self.line
                begin_column = self.column
                in_history = False
                for c in input_generator:
                    if self.wait_completion:
                        self.wait_completion = False
                    # print(c)
                    # continue
                    if c == '<Ctrl-j>':
                        if in_history:
                            text = self.history[history_index]
                            in_history = False

                        if self.read_until in [CR, NL]:
                            self.history.append(text)
                            self.print_result(self.evaluate(text))
                            self.write_xy(self.line + 1, 0, self.prompt)
                        elif self.complete_on in [CR, NL]:
                            self.offer_completions(text)
                        else:
                            text += '\n'
                            #tokens.append(token)
                            self.write_xy(self.line + 1, 0, self.prompt)
                            begin_line = self.line
                            begin_column = self.column
                    elif c == '<UP>':
                        if not in_history:
                            history_index = len(self.history) - 1
                            in_history = True
                        self.write_xy(begin_line, begin_column, self.highlight_text(self.history[history_index]))
                        if history_index > 0:
                            history_index -= 1
                    elif c == '<DOWN>':
                        if in_history:
                            history_index += 1
                        if history_index > len(self.history) - 1:
                            in_history = False
                            self.write_xy(begin_line, begin_column, self.highlight_text(text))
                        else:
                            self.write_xy(begin_line, begin_column, self.highlight_text(self.history[history_index]))

                    elif c == '<LEFT>':
                        if self.column > len(self.prompt):
                            self.column -= 1

                    elif c == '<RIGHT>':
                        if self.column < len(self.prompt) + len(text):
                            self.column += 1

                    elif c == '<BACKSPACE>':
                        if self.column > len(self.prompt):
                            text = text[:-1]
                            self.write_xy(begin_line, begin_column, self.highlight_text(text))

                    elif c == '<Ctrl-D>':
                        if self.history_file:
                            with open(self.history_file, 'a+') as f:
                                f.write('\n'.join(self.history[self.new_history:]) + '\n')
                        exit(0)
                    elif c in ['<SPACE>', '<TAB>'] or len(c) == 1:
                        if in_history:
                            text = self.history[history_index]
                            in_history = False

                        if self.complete_on == c:
                            self.offer_completions(text + c)
                        elif self.read_until == c:
                            self.history.append(text)
                            self.print_result(self.evaluate(text))
                            self.write_xy(self.line + 1, 0, self.prompt)
                            begin_line = self.line
                            begin_column = self.column
                        else:
                            text += c if len(c) == 1 else {'<SPACE>': ' ', '<TAB>': '\t'}[c]
                            if c[0].isalnum():
                                self.write_xy(self.line, self.column, c)
                            else:
                                self.write_xy(begin_line, begin_column, self.highlight_text(text))


                    window.render_to_terminal(self.a)
                    


    def highlight_text(self, text):
        token = ''
        tokens = []
        unal = ''
        for c in text:
            if c.isalnum():
                token += c
                if unal:
                    tokens.append(unal)
                    unal = ''
            else:
                if token:
                    tokens.append(token)
                    token = ''
                unal += c
        if token:
            tokens.append(token)
        if unal:
            tokens.append(unal)
        # print(text,tokens)

        highlighted = []
        for token in tokens:
            if not token[0].isalnum():
                highlighted.append(token)
                continue
            matched = False

            for pattern, color in self.highlight:
                m = re.match(pattern, text)
                if m and m.span()[1] == len(token):
                    # print(pattern)
                
                    matched = True
                    if ' on ' in color:
                        x, y, back = color.partition(' on ')
                        if x:
                            fore = x
                            highlighted.append(
                                getattr(curtsies.fmtfuncs, 'on_' + back)(
                                    getattr(curtsies.fmtfuncs, fore)(
                                        token)))
                        else:
                            highlighted.append(
                                getattr(curtsies.fmtfuncs, 'on_' + back)(token))

                    else:
                        fore = color
                        highlighted.append(
                            getattr(curtsies.fmtfuncs, fore)(token))
                    break

            if not matched:
                highlighted.append(token)
        # print(highlighted)
        return highlighted


    def write_xy(self, line, column, text):
        if not isinstance(text, str):
            size = sum([len(t if isinstance(t, str) else t.s) for t in text])
            text = ''.join(map(str, text))
        else:
            size = len(text)
        self.a[line, column:column+size] = [text]
        self.line = line
        self.column = column + size

    def write(self, text):
        self.a[self.line:self.line + 1, self.column: self.column + len(text)] = text
        self.column += len(text)

    def offer_completions(self, text):
        if self.complete:
            completions = []
        else:
            completions = self.complete(text)
        old_line = self.line            
        for completion in completions:
            self.write_xy(self.line + 1, self.column, str(completion))
        self.line = old_line
        self.wait_completion = True

    def evaluate(self, text):
        return text

    def print_result(self, result):
        self.write_xy(self.line + 1, 0, result)

