import html
from operator import itemgetter
import pathlib
import re
import sqlite3
import typing


HERE = pathlib.Path(__file__).resolve().parent
DB = HERE / 'mkdata.db'


def database_to_table(
    dbfilename: pathlib.Path,
    sql: str, parameters: typing.Tuple[str] = None,
    comma_to_list: bool = True,
    cparse: typing.Callable[[str, str], str] = None
):
    def _parse(val, header):
        if isinstance(val, str):
            val = html.escape(val, quote=False).replace('\n', '<br/>')

        if cparse:
            val = cparse(val, header)

        if val is None:
            return ''

        if comma_to_list and isinstance(val, str) and ',' in val:
            # convert to list
            return '<ul>' + '\n'.join(f'<li>{x}</li>' for x in re.split(r'\s*,\s*', val))

        if isinstance(val, str) and val.startswith('-'):
            # convert to list
            li = re.findall(r'-\s*(.*)', val)
            return '<ul>' + '\n'.join(f'<li>{x}</li>' for x in li) + '</ul>'

        return str(val)

    def _gen():
        with sqlite3.connect(dbfilename) as conn:
            cur = conn.cursor()
            result = cur.execute(sql, parameters or tuple())
            columns = tuple(map(itemgetter(0), result.description))

            yield '<table style="width: 100%;">\n'

            # table header
            width = 100 // len(columns)
            yield '<thead>\n<tr>\n'
            for col in columns:
                yield f'<th style="width: {width}%;">{_parse(col, col)}</th>'
            yield '</tr></thead>'

            # body of table
            yield '<tbody>\n'
            for i, row in enumerate(result, start=1):
                parity = 'even' if i % 2 == 0 else 'odd'
                yield '<tr>\n'
                for col, header in zip(row, columns):
                    yield f'<td class="{parity}" style="width: {width}%;">{_parse(col, header)}</td>'
                yield '</tr>\n'
            yield '</tbody>'

            yield '</table>'

    return '\n'.join(_gen())


def write_collapsible(
    header: str, sid: str,
    dbfilename: pathlib.Path, sql: str, parameters=None,
    comma_to_list: bool = True, cparse: typing.Callable[[str], str] = None
):
    def _gen():
        yield f'<button class="collapsible">{header}</button>'
        yield f'<div class="content" id="{sid}">'
        yield database_to_table(dbfilename, sql, parameters, comma_to_list, cparse)
        yield '</div>'
        yield ''

    return '\n'.join(_gen())


def write_header(header: str, hid: str, level: int = 1):
    return f'<h{level} id="{hid}"">{header}</h{level}>'


def write_minimal_battles():
    def _gen():
        with sqlite3.connect(DB) as conn:
            cur = conn.cursor()
            fight_numbers = sorted(set(
                x[0] for x in cur.execute('SELECT "Fight Number" FROM "Minimal Battles";').fetchall()
            ))

        for fight in fight_numbers:
            yield f'<h2>Fight #{fight}</h2>'
            yield database_to_table(
                DB,
                sql="""
                    SELECT "Count" || "x" AS "Count", "Enemy", "Comment", "HP", "Species", "Weak", "Resist",
                        "Poison", "Sleep", "Curse", "Seal", "Slow", "Spoil", "Snack", "Heart"
                    FROM "Minimal Battles"
                    INNER JOIN "Enemy Data"
                    ON "Minimal Battles"."Enemy" = "Enemy Data"."Name"
                    WHERE "Fight Number" = ?
                """,
                parameters=(fight,)
            )

        yield """<p>
            In order to avoid fighting 「Crazed Eye」, we must avoid inishing a finale character quest and get
            Vayne's ending. Many non-finale character quests (i.e., Philo I/II/III/IV, Nikki I/II, Pamela I, Roxis
            I/II/III/IV, Anna I, and Muppy I/II/III) can still be completed. This means that the following character
            quest trophies can still be obtained on this run:
        </p>"""

        yield """<div>
        <table class="zebra">
        <tr class="trophy-unobtained">
                <td width="7%" style="text-align: center;">
                    <img src="imgs/vayne.png" width="70%">
                </td>
                <td width="75%">
                    <p>
                        <b>With this space, I wish to...</b><br />
                        <i>Enact your final wish.</i>
                    </p>
                </td>
                <td width="15%" style="text-align: center;">
                </td>
                <td width="3%">
                    <img src="../trophies/40-silver.png" width="90%">
                </td>
            </tr>

            <tr class="trophy-unobtained">
                <td width="7%" style="text-align: center;">
                    <img src="imgs/philo.png" width="70%">
                </td>
                <td width="75%">
                    <p>
                        <b>Was it... a joke?</b><br />
                        <i>Learn about Philo's mysterious illness.</i><br /><span class="detail">Complete Philo
                            III.</span>
                    </p>
                </td>
                <td width="15%" style="text-align: center;">
                </td>
                <td width="3%">
                    <img src="../trophies/40-bronze.png" width="90%">
                </td>
            </tr>
            <tr class="trophy-unobtained">
                <td width="7%" style="text-align: center;">
                    <img src="imgs/nikki.png" width="70%">
                </td>
                <td width="75%">
                    <p>
                        <b>Hey!</b><br />
                        <i>Learn how Nikki attracts all the guys.</i><br /><span class="detail">Listen to Nikki's song
                            in the Workshop Hallway after completing Nikki II.</span>
                    </p>
                </td>
                <td width="15%" style="text-align: center;">
                </td>
                <td width="3%">
                    <img src="../trophies/40-bronze.png" width="90%">
                </td>
            </tr>
            <tr class="trophy-unobtained">
                <td width="7%" style="text-align: center;">
                    <img src="imgs/roxis.png" width="70%">
                </td>
                <td width="75%">
                    <p>
                        <b>This is... a Mana's...</b><br />
                        <i>Help Roxis form a contract with the Mana of Light.</i><br /><span class="detail">Complete
                            Roxis II.</span>
                    </p>
                </td>
                <td width="15%" style="text-align: center;">
                </td>
                <td width="3%">
                    <img src="../trophies/40-bronze.png" width="90%">
                </td>
            </tr>
            <tr class="trophy-unobtained">
                <td width="7%" style="text-align: center;">
                    <img src="imgs/muppy.png" width="70%">
                </td>
                <td width="75%">
                    <p>
                        <b>...without this alchemy...</b><br />
                        <i>See Muppy's expulsion overturned and the hostage situation resolved.</i><br /><span
                            class="detail">Complete Muppy III.</span>
                    </p>
                </td>
                <td width="15%" style="text-align: center;">
                </td>
                <td width="3%">
                    <img src="../trophies/40-bronze.png" width="90%">
                </td>
            </tr>
        </table>
        </div>
        </div>
        """

    return '\n'.join(_gen())


def write_sound_data():
    def _gen():
        yield '<button class="collapsible">SOUND/STREAM Data</button>'
        yield '<div class="content" id="sound-stream">'

        yield database_to_table(
                DB,
                sql="""
                    SELECT printf("%03d", "Track Number") as "Track Number", "Track Name", "Description"
                    FROM "Sound Stream"
                """,
                comma_to_list=False
            )

        yield '</div>'

    return '\n'.join(_gen())


SQL_LOOKUPS = {
    'Usable': """
        SELECT "Item Name", "Effect", "Target", "Recipe Location", Recipe, "E-Effect", "Sell", "Location"
        FROM "Item Data"
        WHERE Category = "Usable" AND "Recipe" IS NOT NULL;""",

    'Material': """
        SELECT "Item Name", "Recipe Location", Recipe, "E-Effect", "Sell", "Location"
        FROM "Item Data"
        WHERE Category = "Material" AND "Recipe" IS NOT NULL;
    """,

    'Weapon': """
        SELECT "Item Name", "Users", "Effect", "Recipe Location", Recipe, "Sell", "Location"
        FROM "Item Data"
        WHERE Category = "Weapon" AND "Recipe" IS NOT NULL;
    """,

    'Armor': """
        SELECT "Item Name", "Users", "Effect", "Recipe Location", Recipe, "Sell", "Location"
        FROM "Item Data"
        WHERE Category = "Armor" AND "Recipe" IS NOT NULL;
    """,

    'Accessory': """
        SELECT "Item Name", "Effect", "Recipe Location", Recipe, "E-Effect", "Sell", "Location"
        FROM "Item Data"
        WHERE Category = "Accessory" AND "Recipe" IS NOT NULL;
    """,

    'Key': """
        SELECT "Item Name", "Effect", "Recipe Location", Recipe, "E-Effect", "Sell", "Location"
        FROM "Item Data"
        WHERE Category = "Key" AND "Recipe" IS NOT NULL;
    """,

    'Nonsynthesizable': """
        SELECT "Item Name", "Effect", "Target", "E-Effect", "Sell", "Location", "Category"
        FROM "Item Data"
        WHERE "Recipe" IS NULL;
    """
}


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
    f.write(write_header('Recipe Data', hid='recipe-data'))

    for category in ('Usable', 'Material', 'Weapon', 'Armor', 'Accessory', 'Key'):
        f.write(write_collapsible(
            f'{category}', f'{category}-items',
            dbfilename=DB,
            sql=SQL_LOOKUPS[category]
        ))

    # OTHER DATA
    f.write(write_header('Other Data', hid='other-data'))

    # not synthesized items
    f.write(write_collapsible(
        'Nonsynthesizable Items', 'nonsynthesizable-items',
        dbfilename=DB,
        sql=SQL_LOOKUPS['Nonsynthesizable']
    ))

    # enemy data
    f.write(write_collapsible(
        'Enemy Data', 'enemy-data',
        dbfilename=DB,
        sql="""
            SELECT "Name", "HP", "Species", "Weak", "Resist", "Poison", "Sleep", "Curse", "Seal", "Slow",
            "Location", "Spoil", "Snack", "Heart"
            FROM "Enemy Data"
        """
    ))

    # course data
    f.write(write_collapsible(
        'Course Data', 'course-data',
        dbfilename=DB,
        sql="""
            SELECT "Course Name", "Required", "Instructor", "Description", "Details", "Provided Items", "Hint"
            FROM "Course Data"
        """,
        cparse=lambda val, header: {'YES': '<img src="imgs/required.png">', 'NO': None}.get(val, val)
    ))

    # job data
    f.write(write_collapsible(
        'Job Data', 'job-data',
        dbfilename=DB,
        sql="""
            SELECT "Chapter", printf("%03d", "Job Number") as "Job #", "Job Name", "Client",
                "Request", "Goal", "Reward"
            FROM "Job Data"
            ORDER BY "Chapter", "Job Number"
        """
    ))

    # rumor data
    f.write(write_collapsible(
        'Gossip Shop', 'rumor-data',
        dbfilename=DB,
        sql="""
            SELECT "Rumor Name", "Condition", "Effect", "Cost"
            FROM "Rumor Data"
        """
    ))

    # minimal battles
    f.write('''
    <button class="collapsible">Minimal Battles (Aww, how cute!)</button>
    <div class="content" id="aww-how-cute">

    <div>
        <table class="zebra">
                <tr class="trophy-unobtained">
                <td width="7%" style="text-align: center;">
                    <img src="https://tcrf.net/images/e/e6/Mana_Khemia2_A9_Wmap01.png" width="70%">
                </td>
                <td width="75%">
                    <p>
                        <b>Aww, how cute!</b><br />
                        <i>Complete the game while entering only 22 battles and defeating only 46
                            enemies.</i><br /><span class="detail">Enter only the 22 required battles and defeat only
                            those enemies which must be defeated.
                            Summoned enemies must be prevented when possible.</span>
                    </p>
                </td>
                <td width="15%" style="text-align: center;">

                </td>
                <td width="3%">
                    <img src="../trophies/40-gold.png" width="90%">
                </td>
            </tr>
        </table>
    </div>
''')
    f.write(write_minimal_battles())

    # SOUND/STREAM Data
    f.write(write_sound_data())

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


############################
# write character quests ###
############################
def write_cq(character):
    return write_collapsible(
        character, f'{character.lower()}-cq',
        dbfilename=DB,
        sql="""
            SELECT "Episode", "Chapter " || "Available" AS "Available", "Hook", "Story", "Description"
            FROM "Character Quests"
            WHERE "Name" = ?
            ORDER BY "Episode"
        """,
        parameters=(character,),
        comma_to_list=False
    )


with open(HERE / 'character-quests.html', 'w+') as f:
    f.write("""
    <html>

<head>
    <title>
        MK: Character Quests
    </title>
    <link href="https://fonts.googleapis.com/css?family=Tangerine" rel="stylesheet" />
    <link href="https://fonts.googleapis.com/css?family=Montserrat" rel="stylesheet" />
    <link href="../styles/base-style.css" rel="stylesheet" />
    <link href="style.css" rel="stylesheet" />
    <link rel="icon" href="../favicon.png" type="image/x-icon">
</head>

<body style="font-family: Montserrat, sans-serif;">
    """)

    for character in ('Philo', 'Nikki', 'Pamela', 'Flay', 'Roxis', 'Anna', 'Muppy'):
        f.write(write_cq(character))

    f.write("""
    </body>

</html>""")

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
