import contextlib
import io
import itertools
import pathlib
import re
from typing import List

import poem_helpers


HERE = pathlib.Path(__file__).parent


def bisect_iter(iterable, key=bool):
    a, b = itertools.tee(iter(iterable), 2)
    return itertools.takewhile(key, a), itertools.dropwhile(key, b)


@contextlib.contextmanager
def tag(stream, tagname, **kwargs):
    stream.write(f'<{tagname}')
    stream.write(''.join(f' {k}="{v}"' for k, v in kwargs.items()))
    stream.write('>')

    try:
        yield
    finally:
        stream.write(f'</{tagname}>')


class Poem:
    def __init__(self, title: str, id: str, stanzas: List[List[str]]):
        self.title = title
        self.id = id
        self.stanzas = stanzas

    @classmethod
    def from_file(cls, path: pathlib.Path):
        lines = iter(path.read_text().splitlines())

        # strip out title data
        _title, lines = bisect_iter(lines, lambda line: line.startswith('TITLE'))
        title = '<br/>\n\t'.join(
            parse(re.match(r'TITLE: (.*)', line).group(1))
            for line in _title
        )

        # strip out ID data
        _id, lines = bisect_iter(lines, lambda line: line.startswith('ID'))
        poemid = [
            parse(re.match(r'ID: (.*)', line).group(1))
            for line in _id
        ]
        if len(poemid) == 0:
            raise ValueError(f'No poem ID found in {path}')
        elif len(poemid) > 1:
            raise ValueError(f'Multiple poem IDs found in {path}')

        # parse stanzas
        stanzas = [[]]
        while not (line := next(lines)).rstrip():
            # ignore blank lines at the start
            pass

        lines = [line] + list(lines)

        while lines:
            line = lines.pop(0)

            if (line := line.rstrip()):
                stanzas[-1].append(parse(line))
            else:
                stanzas.append([])

        return cls(title=title, id=poemid[0], stanzas=stanzas)

    def htmlify(self):
        s = io.StringIO()

        s.write(f'<h1 class="title poemtitle" id="{self.id}">\n\t{self.title}\n</h1>\n')
        with tag(s, tagname='div', **{'class': 'poem'}):
            for stanza in self.stanzas:
                with tag(s, tagname='p'):
                    s.write('<br/>\n'.join(stanza))

        s.seek(0)
        return s.read()


def parse(text):
    # handle <ja>...</ja> tags
    text = re.sub(r'<ja>(.*?)</ja>', r'<span class="japanese">\g<1></span>', text)

    # convert **...*** to <b>...</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\g<1></b>', text)

    # convert *...* to <i>...</i>
    text = re.sub(r'\*(.*?)\*', r'<i>\g<1></i>', text)

    # convert _..._ to underline
    text = re.sub(r'_(.*?)_', r'<span class="underline">\g<1></span>', text)

    # handle leading spaces
    text = re.sub(r'^\s+', '&nbsp;&nbsp;', text)

    return text


with open(HERE / 'home.html', 'w+') as f:
    with tag(f, tagname='html'):
        with tag(f, tagname='head'):
            with tag(f, tagname='title'):
                f.write('Humanity of a Former Automaton\n')
            f.write('''<link href="https://fonts.googleapis.com/css?family=Tangerine" rel="stylesheet" />\n''')
            f.write('''<link href="https://fonts.googleapis.com/css?family=Montserrat" rel="stylesheet" />\n''')
            f.write('''<link href="../styles/base-style.css" rel="stylesheet" />\n''')
            f.write('''<link href="style.css" rel="stylesheet" />\n''')
            f.write('''<link rel="icon" href="../favicon.png" type="image/x-icon">''')
            f.write('''<meta name="viewport" content="width=device-width, initial-scale=1">''')

        with tag(f, tagname='body', style='font-family: Montserrat, sans-serif;'):
            # write page title
            with tag(f, tagname='div', **{'class': 'main'}):
                with tag(f, tagname='h1', **{'class': 'title'}):
                    f.write('Humanity of a Former Automaton\n')
                with tag(f, tagname='h2', **{'class': 'title'}):
                    f.write('Lily Ellington\n')

                # write each poem
                navbar = []
                for path in sorted((HERE / 'poems').iterdir(), key=lambda p: p.stem.lower()):
                    poem = Poem.from_file(path)
                    navbar.append(poem)

                    html = poem.htmlify()
                    if (r := poem_helpers.HELPERS.get(poem.title)):
                        html = r(html)
                    f.write(html)

            # build navbar
            with tag(f, tagname='div', **{'class': 'sidenav'}):
                for poem in navbar:
                    f.write(f"""<a href="#{poem.id}">{poem.title}</a><hr class="navdivider">""")
