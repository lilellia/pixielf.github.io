from operator import itemgetter
import pathlib
import sqlite3
import typing


HERE = pathlib.Path(__file__).resolve().parent
DB = HERE / 'mkdata.db'


def database_to_table(dbfilename: pathlib.Path, sql: str, parameters: typing.Tuple[str] = None):
    def _parse(val):
        if val is None:
            return ''
        return str(val)

    def _gen():
        with sqlite3.connect(dbfilename) as conn:
            cur = conn.cursor()
            result = cur.execute(sql, parameters or tuple())
            columns = tuple(map(itemgetter(0), result.description))

            yield '<table>\n'

            # table header
            width = 100 // len(columns)
            yield '<thead>\n<tr>\n'
            for col in columns:
                yield f'<th style="width: {width}%;">{_parse(col)}</th>'
            yield '</tr></thead>'

            # body of table
            yield '<tbody>\n'
            for row in result:
                yield '<tr>\n'
                for col in row:
                    yield f'<td style="width: {width}%;">{_parse(col)}</td>'
                yield '</tr>\n'
            yield '</tbody>'

            yield '</table>'

    return '\n'.join(_gen())


with open(HERE / 'data.html', 'w') as f:
    f.write('''
<html>

<head>
    <title>
        Mana Khemia Data
    </title>
    <link href="https://fonts.googleapis.com/css?family=Tangerine" rel="stylesheet" />
    <link href="https://fonts.googleapis.com/css?family=Montserrat" rel="stylesheet" />
    <link href="../styles/base-style.css" rel="stylesheet" />
    <link href="../styles/trophies.css" rel="stylesheet" />
    <link href="style.css" rel="stylesheet" />
    <link rel="icon" href="../favicon.png" type="image/x-icon">
</head>

<body style="font-family: Montserrat, sans-serif;">
    <p>
        <a class="box" href="mkdata.db">Download SQLite database: mkdata.db</a>
    </p>
''')

    # WRITE RECIPE DATA
    f.write('<h1 id="recipe-data">Recipe Data</h1>')
    f.write('''
<button class="collapsible">Usable Items</button>
<div class="content" id="recipe-data">
''')

    sql = '''
    SELECT "Item Name", "Effect", "Target", "Recipe Location", Recipe, "E-Effect", "Sell", "Location"
    FROM "Item Data"
    WHERE Category = "Usable"
    '''
    f.write(database_to_table(DB, sql))
    f.write('</div>')

    f.write('</body>')

    f.write('''
<script>
    let collapsible = document.getElementsByClassName("collapsible");
    for (let i = 0; i < collapsible.length; i++) {
        collapsible[i].addEventListener("click", function () {
            this.classList.toggle("active");
            let content = this.nextElementSibling;
            if (content.style.display === "block") {
                content.style.display = "none";
            } else {
                content.style.display = "block";
            }
        });
    }
</script>''')
    f.write('</html>')
