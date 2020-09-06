import bs4
import pathlib
import re


class Poem:
    def __init__(self, title, stanzas):
        self.title = title
        self.stanzas = stanzas

    @classmethod
    def from_html(cls, html):
        soup = bs4.BeautifulSoup(html, 'html.parser')
        title = '\n'.join(line.strip() for line in soup.h1.text.strip().splitlines())

        text = soup.find('div', {'class': 'poem'})
        stanzas = [
            [line.strip() for line in p.text.splitlines() if line.strip()]
            for p in text.findAll('p')
        ]

        return cls(title=title, stanzas=stanzas)

    @property
    def head(self):
        return self.title.splitlines()[0].replace(' ', '-').lower()

    def __str__(self):
        title = self.title.replace('\n', '<br/>')
        heading = f'\n\n<!-- {title}-->\n<h1 class="title poemtitle" id="{self.head}">{title}</h1>\n'

        poem = '<div class="poem">\n'
        for stanza in self.stanzas:
            s = '<br/>\n'.join(stanza)
            poem += f'<p>\n{s}\n</p>\n'

        return heading + poem + '</div>'


def get_poems():
    def _key(path: pathlib.Path) -> str:
        m = re.match(r'(?P<ddlc_prefix>\[.*\]_)?(?P<actual_key>.*)', path.stem)
        return m.group('actual_key')

    return [
        Poem.from_html(p.read_text())
        for p in sorted(pathlib.Path('poems').iterdir(), key=_key)
    ]


with open('refactored.html', 'w+') as f:
    # write the page header
    f.write('''\
<html>
<head>
    <title>
        Humanity of a Former Automaton
    </title>
    <link href="https://fonts.googleapis.com/css?family=Tangerine" rel="stylesheet" />
    <link href="https://fonts.googleapis.com/css?family=Montserrat" rel="stylesheet" />
    <link href="style.css" rel="stylesheet" />
    <link rel="icon" href="../favicon.png" type="image/x-icon">
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>

<body style="font-family: Montserrat, sans-serif;">
    <h1 class="title" style="text-align: center;">
        Humanity of a Former Automaton
    </h1>
    <h2 class="title" style="text-align: center;">
        Lily Ellington
    </h2>

    <div class="main">
''')

    # write out all of the poems
    for p in get_poems():
        f.write(str(p))

    f.write('</div>\n')

    # create the navbar
    f.write('\n<div class="sidenav">\n')
    for p in get_poems():
        title = p.title.replace('\n', '<br/>')
        f.write(f'<a href="#{p.head}">{title}</a>\n')
    f.write('</div> <!-- navbar -->\n')

    # write out the page closer
    f.write('</body></html>')
