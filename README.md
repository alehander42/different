#different

Different is a library for building powerful repl-s in python.

It is inspired by standard library's `cmd` but it adds 

* character-level hooks
* easy realtime highlighting
* easy permanent history handling

## example

```python


class BioHackRepl(Repl):
    
    intro = 'a biohacker shell for human nanobot updates'
    prompt = 'biohack> '
    complete_on = TAB
    read_until = '!'
    history_file='.biohack_history'

    highlight = [
        ('human',   'yellow'),
        (r'[0-9]+', 'green'),
        (r'\w+',    'blue on green'),
        ('end',     'red')
    ]

    def on_char(self, buffer):
        if buffer == '?':
            self.rewrite_buffer('erasing current line')

    def eval(self, text):
        return random.choice(['woah human', 'calm yo tits', 'update applied', 'hehe sweety'])

    def print_result(self, result):
        self.display_in_right(result)

    def complete(self, buffer):
        return [line for line in self.history if line.startswith(buffer)]

BioHackRepl().loop()

```
## todo

- [ ] make it usable

## why

it's almost impossible to use the standard cmd module with readline and to 
highlight the input, and `different` can add a lot more niceties
(created while building marvin's cli interface)

## license

MIT License, Alexander Ivanov, 2016
