import contextlib
import io
import json
import numpy as np
import pathlib
import pandas as pd
import re


def romanize(n):
    def fmt(k, one: str, five: str, ten: str):
        lookup = [
            '', f'{one}', f'{one}{one}', f'{one}{one}{one}', f'{one}{five}',
            f'{five}', f'{five}{one}', f'{five}{one}{one}', f'{five}{one}{one}{one}', f'{one}{ten}'
        ]
        return lookup[k]

    roman = ''
    while n >= 1000:
        roman += 'M'
        n -= 1000

    hundreds, n = divmod(n, 100)
    roman += fmt(hundreds, one='C', five='D', ten='M')

    tens, n = divmod(n, 10)
    roman += fmt(tens, one='X', five='L', ten='C')
    roman += fmt(n, one='I', five='V', ten='X')

    return roman


def htmlify_recipe(item, headers):
    def _gen():
        for head, width in headers.items():
            val = item[head]

            if head == 'Ingredients':
                # format as list
                try:
                    val = '<p><ul>' + '\n\t'.join(f'<li>{i}</li>' for i in val) + '</ul></p>'
                except TypeError:
                    val = None
            elif head in ('User', 'Stats'):
                # format as list
                try:
                    val = '<p><ul>' + '\n\t'.join(f'<li>{i}</li>' for i in re.split(r',\s*', val)) + '</ul></p>'
                except TypeError:
                    val = None
            elif head == 'Sell':
                # try to convert to int
                with contextlib.suppress(ValueError):
                    val = int(float(val))

            yield f'<td style="width: {width}%;">{val}</td>'
    return '<tr>' + '\n\t'.join(_gen()) + '</tr>'


recipes = json.loads(pathlib.Path('raw_data/recipe-data.json').read_text())
itemdata = pd.read_csv('raw_data/item-data.csv', index_col=0)
course_data = pd.read_csv('raw_data/course-data.csv')
enemy_data = pd.read_csv('raw_data/enemy-data.csv')


def find_recipe(item):
    for r in recipes:
        if r['item_name'] == item:
            return r
    raise ValueError(f'Cannot find recipe for item {item!r}')


def build_recipes():
    categories = {
        'Usable': {
            'Name': 12,
            'Synthesis': 12,
            'Recipe Location': 12,
            'Ingredients': 56,
            'Sell': 8
        },

        'Material': {
            'Name': 12,
            'Synthesis': 12,
            'Recipe Location': 12,
            'Ingredients': 56,
            'Sell': 8
        },

        'Weapon': {
            'Name': 12,
            'Synthesis': 12,
            'Recipe Location': 12,
            'Ingredients': 40,
            'User': 8,
            'Stats': 8,
            'Sell': 8
        },

        'Armor': {
            'Name': 12,
            'Synthesis': 12,
            'Recipe Location': 12,
            'Ingredients': 40,
            'User': 8,
            'Stats': 8,
            'Sell': 8
        },

        'Accessory': {
            'Name': 12,
            'Synthesis': 12,
            'Recipe Location': 12,
            'Ingredients': 40,
            'User': 8,
            'Stats': 8,
            'Sell': 8
        },

        'Key': {
            'Name': 12,
            'Synthesis': 12,
            'Recipe Location': 12,
            'Ingredients': 56,
            'Sell': 8
        }
    }

    stream = io.StringIO()
    for category, headers in categories.items():
        # write the HTML header for this category
        stream.write(f'''
        <button type="button" class="collapsible">{category} Items</button>
        <div class="content">
            <table>
            <tr>
''')
        for head, width in headers.items():
            stream.write(f'<th style="width: {width}%;">{head}</th>\n')
        stream.write('</tr>\n')

        # get the synthesizable items which fit into the given category
        filtered = itemdata[(itemdata.Category == category)].dropna(subset=('Synthesis',))
        for row in filtered.to_dict(orient='record'):
            item = {
                k: row.get(k, None)
                for k in headers.keys()
            }
            r = find_recipe(row['Name'])
            item['Recipe Location'] = r['recipe_location']
            item['Ingredients'] = r['ingredients']
            stream.write(htmlify_recipe(item, headers) + '\n')
        stream.write('</table></div>')

    with open('x.txt', 'w+') as f:
        stream.seek(0)
        f.write(stream.read())


def htmlify_char_quest(episode, quest):
    def _paragraphize(text):
        if '\n' in text:
            return '\n'.join(
                f'<p>{para}</p>'
                for para in text.split('\n')
            )
        return text

    available = quest.get('available', '')
    hook = quest.get('hook', '')
    description = quest.get('description', '')
    story = quest.get('story', '')
    return f'''<tr>
                <td style="width: 5%;">{romanize(episode)}</td>
                <td style="width: 5%;">{available}</td>
                <td style="width: 10%;">{hook}</td>
                <td style="width: 40%;">{_paragraphize(description)}</td>
                <td style="width: 40%;">{_paragraphize(story)}</td>
            </tr>'''


def build_character_quests():
    stream = io.StringIO()

    with open('raw_data/character-quests.json') as r:
        quests = json.load(r)

    for character in ('Philo', 'Nikki', 'Pamela', 'Flay', 'Roxis', 'Anna', 'Muppy'):
        stream.write(f'''
    <!-- {character} -->
    <button type="button" class="collapsible">
        <img class="icon" src="imgs/{character.lower()}.png" width="75" height="75">
        {character}
    </button>
    <div class="content">
        <table>
            <tr>
                <th style="width: 5%;">Episode</th>
                <th style="width: 5%;">Available</th>
                <th style="width: 10%;">Hook</th>
                <th style="width: 40%;">Description</th>
                <th style="width: 40%;">Story</th>
            </tr>
''')
        filtered = quests.get(character, [])

        for i, quest in enumerate(filtered):
            stream.write(htmlify_char_quest(i+1, quest) + '\n')
        stream.write('</table></div>')

    with open('y.txt', 'w+') as f:
        stream.seek(0)
        f.write(stream.read())


def build_courses():
    def _paragraphize(text):
        if isinstance(text, float):
            # np.nan
            return ''

        if '\n' in text:
            return '\n'.join(f'<p>{para}</p>' for para in text.splitlines())
        else:
            return text

    stream = io.StringIO()
    stream.write('''
    <h1>Course Data</h1>
    <div>
    <table>
        <tr>
            <th style="width: 5%;">Chapter</th>
            <th style="width: 15%;">Name</th>
            <th style="width: 30%;">Description</th>
            <th style="width: 50%;">Guide</th>
        </tr>
''')

    for row in course_data.to_dict(orient='record'):
        chapter = row.get('Chapter', '')
        name = row.get('Course', '')
        description = row.get('Description', '')
        guide = row.get('Hint', '')

        stream.write(f'''
        <tr>
            <th style="width: 5%;">{chapter}</th>
            <th style="width: 15%;">{name}</th>
            <th style="width: 30%;">{_paragraphize(description)}</th>
            <th style="width: 50%;">{_paragraphize(guide)}</th>
        </tr>
''')

    stream.write('</table></div>')

    with open('x.txt', 'w+') as f:
        stream.seek(0)
        f.write(stream.read())


def build_enemies():
    def _paragraphize(text):
        if isinstance(text, float):
            return '' if np.isnan(text) else int(text)

        if ',' in text:
            return '<p><ul>' + '\n'.join(f'<li>{item}</li>' for item in text.split(', ')) + '</ul></p>'
        else:
            return text

    stream = io.StringIO()
    stream.write('''
    <div><table>
    <tr>
        <th style="width: 9%;">Name</th>
        <th style="width: 5%;">HP</th>
        <th style="width: 5%;">AP</th>
        <th style="width: 5%;">Cole</th>
        <th style="width: 5%;">Species</th>
        <th style="width: 5%;">Weak</th>
        <th style="width: 5%;">Resist</th>
        <th style="width: 15%;">Protections</th>
        <th style="width: 15%;">Location</th>
        <th style="width: 12%;">Spoil</th>
        <th style="width: 11%;">Snack</th>
        <th style="width: 5%;">Heart</th>
    </tr>
''')

    def _imagify(lst):
        if isinstance(lst, float) and np.isnan(lst):
            return ''

        lst = lst.split(', ')
        imgs = ''.join(
            f'<img src="imgs/{item.lower()}.png" width="15" height="15">'
            for item in lst
        )
        return f'<p>{imgs}</p>'

    for row in enemy_data.to_dict(orient='record'):
        name = row.get('Name', '')
        hp = row.get('HP', '')
        ap = row.get('AP', '')
        cole = row.get('Cole', '')
        species = row.get('Species', '')
        weak = row.get('Weak', '')
        resist = row.get('Resist', '')
        protections = row.get('Protections', '')
        location = row.get('Location', '')
        spoil = row.get('Spoil', '')
        snack = row.get('Snack', '')
        heart = row.get('Heart', '')

        stream.write(f'''
    <tr>
        <td style="width: 9%;">{_paragraphize(name)}</td>
        <td style="width: 5%;">{hp:,}</td>
        <td style="width: 5%;">{ap:,}</td>
        <td style="width: 5%;">{cole:,}</td>
        <td style="width: 5%;">{_paragraphize(species)}</td>
        <td style="width: 5%;">{_imagify(weak)}</td>
        <td style="width: 5%;">{_imagify(resist)}</td>
        <td style="width: 15%;">{_imagify(protections)}</td>
        <td style="width: 15%;">{_paragraphize(location)}</td>
        <td style="width: 12%;">{_paragraphize(spoil)}</td>
        <td style="width: 11%;">{_paragraphize(snack)}</td>
        <td style="width: 5%;">{_paragraphize(heart)}</td>
    </tr>
''')

    stream.write('</table></div>')

    with open('x.txt', 'w+') as f:
        stream.seek(0)
        f.write(stream.read())


# build_recipes()
# build_character_quests()
# build_courses()
build_enemies()
