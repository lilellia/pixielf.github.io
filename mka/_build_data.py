import io
import json
import re
import pandas


class Recipe:
    def __init__(self, recipe, location, itemName, ingredients):
        self.recipe = recipe
        self.location = location
        self.item = itemName
        self.ingredients = ingredients

    def pretty(self, i):
        ingr = '\n'.join(f'<li>{i}</li>' for i in self.ingredients)
        color = 'even' if i % 2 == 0 else 'odd'
        return f'''
    <tr>
        <td class="{color}" style="width: 12%;"><b>{self.item}</b></td>
        <td class="{color}" style="width: 12%;">{self.recipe}</td>
        <td class="{color}" style="width: 12%;">{self.location}</td>
        <td class="{color}" style="width: 64%;"><p><ul>{ingr}</ul></p></td>
    </tr>
'''


def find_recipe(lookup, item):
    g = (r for r in lookup if r['itemName'] == item)
    return next(g, None)


def build_recipes():
    stream = io.StringIO()
    items = pandas.read_csv('raw_data/item-data.csv', index_col=0)
    with open('raw_data/recipe-data.json', 'r') as f:
        recipes = json.load(f)

    for category in ('Usable', 'Material', 'Weapons', 'Armor', 'Accessory', 'Key'):
        stream.write(f'''
    <button type="button" class="collapsible">{category} Items</button>
    <div class="content">
    <table>
    <tr>
        <th style="width: 12%;">Item Name</th>
        <th style="width: 12%;">Recipe Name</th>
        <th style="width: 12%;">Recipe Location</th>
        <th style="width: 64%;">Ingredients</th>
    </tr>
''')
        filtered = items[items.Category == category]
        i = 0
        for item in filtered.Name:
            if not (k := find_recipe(recipes, item)):
                continue

            stream.write(Recipe(**k).pretty(i))
            i += 1

        stream.write('</table></div>')

    with open('x.txt', 'w+') as f:
        stream.seek(0)
        f.write(stream.read())


build_recipes()
