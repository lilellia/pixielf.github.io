import contextlib
import html
import io
import json
import pathlib
import re
import sqlite3
from typing import Optional, Tuple


HERE = pathlib.Path(__file__).resolve().parent
DB = HERE / 'mkdata.db'


def db_query(database: pathlib.Path, sql: str, args: Optional[Tuple[str]] = None):
    with sqlite3.connect(database) as conn:
        c = conn.cursor()
        records = c.execute(sql, args or tuple())
        columns = tuple(z[0] for z in records.description)

        return columns, tuple(records)


class HTMLWriter:
    def __init__(self):
        self._stream = io.StringIO()

    def write(self, text: str, end: str = '\n'):
        self._stream.write(text + end)

    def __str__(self):
        self._stream.seek(0)
        text = self._stream.read()
        self._stream.seek(0, io.SEEK_END)
        return text

    def export_to(self, path: pathlib.Path):
        pathlib.Path(path).write_text(str(self))

    @contextlib.contextmanager
    def wraptag(self, tag, **kwargs):
        if kwargs:
            classes = [
                kwargs.pop('class', None),
                kwargs.pop('class_', None)
            ]
            kwargs['class'] = ' '.join(c for c in classes if c)
            kws = ' '.join(f'{k}="{v}"' for k, v in kwargs.items() if v)
            self.write(f'<{tag} {kws}>')
        else:
            self.write(f'<{tag}>')

        try:
            yield
        finally:
            self.write(f'</{tag}>')

    @contextlib.contextmanager
    def collapsible(self, header: str, class_: str = None, id_: str = None):
        if class_:
            btn_class_ = f'collapsible {class_}'
        else:
            btn_class_ = 'collapsible'

        with self.wraptag('button', class_=btn_class_, id=id_):
            self.write(header)

        class_ = f'content {class_}' if class_ else 'content'
        with self.wraptag('div', class_=class_, id=id_):
            try:
                yield
            finally:
                pass

    @staticmethod
    def _parse(value, comma_to_list: bool = True):
        if isinstance(value, str):
            value = html.escape(value, quote=False)

        if value is None:
            return ''

        if not isinstance(value, str):
            return str(value)

        if value.startswith('-'):
            # convert to list
            _, *items = re.split(r'\s+-\s+', value)
            return '<ul>' + '\n'.join(f'<li>{x}</li>' for x in items) + '</ul>'

        if comma_to_list and ',' in value:
            items = re.split(r'\s*,\s*', value)
            return '<ul>' + '\n'.join(f'<li>{x}</li>' for x in items) + '</ul>'

        return '\n'.join(f'<p>{line}</p>' for line in value.splitlines())

    def database_query(
        self,
        db: pathlib.Path,
        sql: str,
        args: Optional[Tuple[str]] = None,
        comma_to_list: bool = True
    ):
        columns, records = db_query(DB, sql, args or tuple())
        with self.wraptag('table', style='width: 100%;'):
            each, marginal = divmod(100, len(columns))

            # table header
            with self.wraptag('thead'):
                with self.wraptag('tr'):
                    for i, colhead in enumerate(columns):
                        w = (each + marginal) if i == 0 else each
                        with self.wraptag('th', style=f'width: {w}%;'):
                            self.write(self._parse(colhead, comma_to_list=comma_to_list))

            # table body
            with self.wraptag('tbody'):
                for i, row in enumerate(records, start=1):
                    parity = 'even' if i % 2 == 0 else 'odd'
                    with self.wraptag('tr'):
                        for j, val in enumerate(row):
                            w = (each + marginal) if j == 0 else each
                            with self.wraptag('td', class_=parity, style=f'width: {w}%;'):
                                self.write(self._parse(val, comma_to_list=comma_to_list))

    def allow_collapsible(self):
        with self.wraptag('script'):
            self.write('''
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
            ''')


SQL_LOOKUPS = json.loads((HERE / 'htmlify.json').read_text())


def write_minimal_battles(w: HTMLWriter):
    with w.collapsible(header='Minimal Battles (Aww, how cute!)', id_='aww-how-cute'):
        w.write('''
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
                                 enemies.</i><br /><span class="detail">Enter only the 22 required battles and
                                 defeat only those enemies which must be defeated. Summoned enemies must be
                                 prevented when possible.</span>
                            </p>
                        </td>
                        <td width="15%" style="text-align: center;"></td>
                        <td width="3%">
                            <img src="../trophies/40-gold.png" width="90%">
                        </td>
                    </tr>
                </table>
            </div>
        ''')

        for f in range(1, 24):
            sql = """
                SELECT "Chapter", "Week", "Context"
                FROM "Minimal Battles"
                WHERE "Fight Number" = ?;
            """
            columns, records = db_query(DB, sql=sql, args=(f,))
            chapter, week, context = records[0]

            with w.wraptag('h2'):
                w.write(f'Fight #{f:02}')

            with w.wraptag('p'):
                with w.wraptag('b'):
                    w.write(f'Chapter {chapter}, Week {week}')
                w.write('<br/>')
                w.write(context)

            sql = """
                SELECT "Enemy" || (CASE "Count" WHEN "1" THEN " " ELSE " [x" || "Count" || "]" END) AS "Enemy",
                    "Comment", "HP", "Species", "Weak", "Resist",
                    TRIM(
                           (CASE WHEN Poison IS NULL THEN "" ELSE 'Poison, '	END)
                        || (CASE WHEN Sleep IS NULL THEN "" ELSE 'Sleep, ' END)
                        || (CASE WHEN Curse IS NULL THEN "" ELSE 'Curse, ' END)
                        || (CASE WHEN Seal IS NULL THEN "" ELSE 'Seal, ' END)
                        || (CASE WHEN Slow IS NULL THEN "" ELSE 'Slow' END)
                    , " ,") AS "Protections",
                    "Spoil", "Snack", "Heart"
                FROM "Minimal Battles" INNER JOIN "Enemy Data" ON "Minimal Battles"."Enemy" = "Enemy Data"."Name"
                WHERE "Fight Number" = ?;
            """
            w.database_query(DB, sql, args=(f,))

        with w.wraptag('p'):
            w.write(""" In order to avoid fighting 「Crazed Eye」, we must avoid inishing a finale character quest and
                get Vayne's ending. Many non-finale character quests (i.e., Philo I/II/III/IV, Nikki I/II, Pamela I,
                Roxis I/II/III/IV, Anna I, and Muppy I/II/III) can still be completed. This means that the following
                character quest trophies can still be obtained on this run:""")

        # write obtainable CQ trophies
        w.write("""
            <div>
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
                        <td width="15%" style="text-align: center;"></td>
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
                        <td width="15%" style="text-align: center;"></td>
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
                                <i>Learn how Nikki attracts all the guys.</i><br /><span class="detail">
                                    Listen to Nikki's song in the Workshop Hallway after completing Nikki II.</span>
                            </p>
                        </td>
                        <td width="15%" style="text-align: center;"></td>
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
                                <i>Help Roxis form a contract with the Mana of Light.</i><br />
                                <span class="detail">Complete Roxis II.</span>
                            </p>
                        </td>
                        <td width="15%" style="text-align: center;"></td>
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
        """)


def write_data():
    w = HTMLWriter()
    with w.wraptag('html'):
        with w.wraptag('head'):
            with w.wraptag('title'):
                w.write('Mana Khemia Data')
            w.write('''
                <link href="https://fonts.googleapis.com/css?family=Tangerine" rel="stylesheet" />
                <link href="https://fonts.googleapis.com/css?family=Montserrat" rel="stylesheet" />
                <link href="../styles/base-style.css" rel="stylesheet" />
                <link href="../styles/trophies.css" rel="stylesheet" />
                <link href="style.css" rel="stylesheet" />
                <link rel="icon" href="../favicon.png" type="image/x-icon">
            ''')

        with w.wraptag('body', style='font-family: Montserrat, sans-serif;'):
            with w.wraptag('p'):
                with w.wraptag('a', class_='box', href='mkdata.db'):
                    w.write('Download SQLite database, mkdata.db')

            # write recipe data
            with w.wraptag('h1', id='recipe-data'):
                w.write('Recipe Data')
            for cat in ('Usable', 'Material', 'Weapon', 'Armor', 'Accessory', 'Key'):
                with w.collapsible(header=cat, id_=f'{cat.lower()}-recipes'):
                    sql, ctl = SQL_LOOKUPS[cat]
                    w.database_query(DB, sql=sql, comma_to_list=ctl)

            # other data
            with w.wraptag('h1', id='other-data'):
                w.write('Other Data')

            for cat in ('Nonsynthesizable Item', 'Enemy', 'Course', 'Job', 'Gossip Shop', 'SOUND-STREAM'):
                with w.collapsible(header=f'{cat} Data', id_=f'{cat.lower()}-data'):
                    sql, ctl = SQL_LOOKUPS[cat]
                    w.database_query(DB, sql=sql, comma_to_list=ctl)

            # minimal battles
            write_minimal_battles(w)

    w.allow_collapsible()
    w.export_to(HERE / 'data.html')


def write_endings(w: HTMLWriter, character: str):
    sql, ctl = SQL_LOOKUPS['Character Ending']
    _, records = db_query(DB, sql, args=(character,))

    def _write_row(icon, text):
        with w.wraptag('td', class_='cqe-icon'):
            w.write(icon or '')

        s = 'dialogue' if icon else 'stage-dir'
        with w.wraptag('td', class_=f'cqe-{s}'):
            w.write(text)

    with w.wraptag('div'):
        with w.wraptag('table', style='width: 100%;'):
            for speaker, line in records:
                if (HERE / (p := f'imgs/{speaker}.png'.lower().replace(' ', '-'))).exists():
                    speaker = f'<img src="{p}" width="75">'

                with w.wraptag('tr'):
                    text = w._parse(line, comma_to_list=False)
                    _write_row(speaker, text)


def write_character_quests():
    w = HTMLWriter()

    with w.wraptag('html'):
        with w.wraptag('head'):
            with w.wraptag('title'):
                w.write('Mana Khemia Data')
            w.write('''
                <link href="https://fonts.googleapis.com/css?family=Tangerine" rel="stylesheet" />
                <link href="https://fonts.googleapis.com/css?family=Montserrat" rel="stylesheet" />
                <link href="../styles/base-style.css" rel="stylesheet" />
                <link href="../styles/trophies.css" rel="stylesheet" />
                <link href="style.css" rel="stylesheet" />
                <link rel="icon" href="../favicon.png" type="image/x-icon">
            ''')

        with w.wraptag('body', style='font-family: Montserrat, sans-serif;'):
            for char in ('Philo', 'Nikki', 'Pamela', 'Flay', 'Roxis', 'Anna', 'Muppy'):
                with w.collapsible(
                    header=f'<img src="imgs/{char.lower()}.png" width="100"> {char}',
                    class_=f'cq-{char.lower()}', id_=f'cq-{char.lower()}'
                ):
                    with w.wraptag('h2'):
                        w.write('CQ Episodes')
                    sql, ctl = SQL_LOOKUPS['Character Quest']
                    w.database_query(DB, sql, args=(char,), comma_to_list=ctl)

                    with w.wraptag('h2'):
                        w.write('Ending')
                    write_endings(w, character=char)

            # add Vayne ending
            char = 'Vayne'
            with w.collapsible(
                    header=f'<img src="imgs/{char.lower()}.png" width="100"> {char}',
                    class_=f'cq-{char.lower()}', id_=f'cq-{char.lower()}'
            ):
                with w.wraptag('h2'):
                    w.write('Ending')
                write_endings(w, character=char)

    w.allow_collapsible()
    w.export_to(HERE / 'character-quests.html')


write_data()
write_character_quests()
