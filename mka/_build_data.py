import contextlib
import io
import itertools
import json
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
    available = quest.get('available', '')
    hook = quest.get('hook', '')
    description = quest.get('description', '')
    story = quest.get('story', '')
    return f'''<tr>
                <td style="width: 5%;">{romanize(episode)}</td>
                <td style="width: 5%;">{available}</td>
                <td style="width: 10%;">{hook}</td>
                <td style="width: 40%;">{description}</td>
                <td style="width: 40%;">{story}</td>
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

        for i, quest in itertools.zip_longest(range(5), filtered, fillvalue=dict()):
            stream.write(htmlify_char_quest(i+1, quest) + '\n')
        stream.write('</table></div>')

    with open('y.txt', 'w+') as f:
        stream.seek(0)
        f.write(stream.read())


# build_recipes()
build_character_quests()
