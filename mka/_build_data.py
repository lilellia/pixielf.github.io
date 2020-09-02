import contextlib
import io
import json
import pathlib
import pandas as pd
import re


def htmlify(item, headers):
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
                    val = '<p><ul>' + '\n\t'.join(f'<li>{i}</li>' for i in re.split(',\s*', val)) + '</ul></p>'
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
            stream.write(htmlify(item, headers) + '\n')

    with open('x.txt', 'w+') as f:
        stream.seek(0)
        f.write(stream.read())


build_recipes()