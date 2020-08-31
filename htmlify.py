import collections
import bs4
import itertools
import pathlib
import re
import sys


PoemEntry = collections.namedtuple('PoemEntry', ('title', 'link'))
INDEX = pathlib.Path('index.html')


def htmlify(title: str, latex: str) -> str:
    # top, header bit
    html = f'''<html>
    <head>
        <title>HFA: {title}</title>
        <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Tangerine">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Montserrat">
        <link rel="stylesheet" href="../style.css">
    </head>

    <div class="topnav">
        <a class="active" href="../../index.html">Back</a>
    </div>

    <h1 class="title">{title}</h1>

    <div class="poem">
        <p>
'''

    def delatexify(s):
        return re.sub(r'\\hspace\*\{.*?\}', '&nbsp;', s).replace(r'``', '"').replace(r"''", '"')

    # the actual poem part
    for line in latex.splitlines():
        if not line.strip():
            continue
        if (m := re.fullmatch(r'\s*(.*)\s*\\\\', line)):
            # normal line in stanza
            s = delatexify(m.group(1))
            html += f"{' ' * 12}{s}<br/>\n"
        elif (m := re.fullmatch(r'\s*(.*)\s*\\\\!', line)):
            # last line in stanza
            s = delatexify(m.group(1))
            html += f"{' ' * 12}{s}<br/>\n{' ' * 8}</p>\n{' ' * 8}<p>\n"
        else:
            # probably last line of poem
            s = delatexify(line.strip())
            html += f"{' ' * 12}{s}\n{' ' * 8}</p>\n"

    # the bottom bit
    html += '''\
    </div>
</html>
'''

    return html


def insert(title, filepath):
    html = INDEX.read_text()
    soup = bs4.BeautifulSoup(html, 'html.parser')

    # get all the existing poems, then add the new one to this list
    poem_list = soup.find('ul', dict(id='poem-list'))
    poems = [
        PoemEntry(poem.a.text, poem.a['href'])
        for poem in poem_list.findAll('li')
    ] + [
        PoemEntry(title, str(filepath))
    ]

    # sort the poems alphabetically by the first alphabetic character in their title
    # ignoring anything in brackets
    def key(poem):
        t = re.sub(r'\[.*?\]', '', poem.title)
        g = itertools.dropwhile(lambda char: re.match('[A-Za-z]', char) is None, t)
        return ''.join(g).upper()

    poems.sort(key=key)
    new_list = soup.new_tag('ul', id='poem-list')
    for title, link in poems:
        li = soup.new_tag('li')
        a = soup.new_tag('a', href=link)
        a.string = title
        li.append(a)
        new_list.append(li)

    poem_list.replace_with(new_list)
    INDEX.write_text(soup.prettify())


def main():
    title = input('Poem Title: ')

    print('Enter LaTeX verse text:')
    html = htmlify(title, sys.stdin.read())

    filepath = f'static/poems/{title.lower().replace(" ", "_")}.html'
    with open(filepath, 'w+') as f:
        f.write(html)

    insert(title, filepath)


if __name__ == '__main__':
    main()
