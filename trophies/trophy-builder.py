import collections
import contextlib
import datetime
import enum
import io
import pathlib
import sqlite3
from typing import List, Optional


HERE = pathlib.Path(__file__).resolve().parent
DBFILENAME = HERE / pathlib.Path("trophies.db")


class TrophyLevel(enum.Enum):
    BRONZE = dict(id=0, score=15)
    SILVER = dict(id=1, score=30)
    GOLD = dict(id=2, score=90)
    PLATINUM = dict(id=3, score=180)

    @classmethod
    def from_id(cls, id: int):
        for level in cls:
            if level.value["id"] == id:
                return level
        else:
            raise ValueError("No TrophyLevel found with id={id!r}")

    @classmethod
    def descending(cls):
        return sorted(cls, key=lambda e: e.value["id"], reverse=True)


class Trophy:
    def __init__(
        self,
        img_source: str,  # link to trophy icon image
        name: str,  # name of trophy
        description: str,  # required task
        details: Optional[str],  # any additional details
        obtained: Optional[str],  # date/time it was obtained (None for unobtained)
        level: int,  # level (0 for bronze, ...)
    ):
        self.img_source = img_source
        self.name = name
        self.description = description
        self.details = details
        self.obtained = self.parse_obtained(obtained)
        self.level = TrophyLevel.from_id(level)

    @staticmethod
    def parse_obtained(obtained):
        if obtained is None:
            return ''
        if obtained == '✓':
            return '✓'
        return datetime.datetime.strptime(obtained, "%m/%d/%Y %H:%M")

    @property
    def score(self):
        """ The number of points earned for this trophy. """
        return self.level.value["score"] if self.obtained else 0

    @property
    def weight(self):
        """ The total number of points possible for achieving this trophy. """
        return self.level.value["score"]


def get_game_data(dbfilename: pathlib.Path) -> dict:
    """ Get all the game data from the database. """
    with contextlib.closing(sqlite3.connect(dbfilename)) as conn:
        with conn as cur:
            result = cur.execute("SELECT * FROM GAMELOOKUP;")
            columns = [desc[0] for desc in result.description]
            games = [dict(zip(columns, game)) for game in result]

            # add trophies to this game dict
            for game in games:
                table = game["TableName"]
                trophies = [
                    Trophy(*t) for _, *t in cur.execute(f"SELECT * FROM {table}")
                ]

                game["trophies"] = trophies

            return games


def count_trophies(trophies):
    result = collections.defaultdict(lambda: collections.defaultdict(int))
    for trophy in trophies:
        result[trophy.level]["total"] += 1
        result[trophy.level]["obtained"] += int(bool(trophy.obtained))

    return result


def write_header(stream: io.StringIO, game: dict):
    stream.write(
        f"""\
<html>

<head>
    <title>
        {game['GameName']} Trophies
    </title>
    <link href="https://fonts.googleapis.com/css?family=Tangerine" rel="stylesheet" />
    <link href="https://fonts.googleapis.com/css?family=Montserrat" rel="stylesheet" />
    <link href="../styles/base-style.css" rel="stylesheet" />
    <link href="../styles/trophies.css" rel="stylesheet" />
    <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
    <link rel="icon" href="../favicon.png" type="image/x-icon">
</head>"""
    )

    counts = count_trophies(game["trophies"])
    obtained = sum(v["obtained"] for v in counts.values())
    total = sum(v["total"] for v in counts.values())

    stream.write(
        f"""
<body style="font-family: Montserrat, sans-serif;">
    <div>
        <!-- header -->
        <table class="zebra">
            <tr>
                <td width="10%" style="text-align: center;"><img src="imgs/gamelogo.png" width="95%"></td>
                <td width="75%"><b style="font-size: 200%;">{game['GameName']}</b></td>
                <td width="3%"><img src="../trophies/complete-icon-{"on" if obtained == total else "off"}.png"></td>
                <td width="13%;">{obtained}/{total} trophies obtained</td>
            </tr>
            <tr>
                <td></td>
                <td>"""
    )

    for level in TrophyLevel.descending():
        a = counts[level]["obtained"]
        b = counts[level]["total"]
        stream.write(
            f"""
                    <img src="../trophies/40-{level.name.lower()}.png"> {a}/{b}
"""
        )
    stream.write(
        """
                </td>
            </tr>
        </table>
"""
    )


def write_trophies(stream: io.StringIO, trophies: List[Trophy]):
    stream.write('<table class="zebra">')

    for trophy in trophies:
        details = f'<br/><span class="detail">{trophy.details}</span>' if trophy.details else ''
        if trophy.obtained:
            if isinstance(trophy.obtained, datetime.datetime):
                obtained = trophy.obtained.strftime('%m/%d/%Y %H:%M')
            else:
                # not a datetime object
                obtained = str(trophy.obtained)
        else:
            obtained = ''
        stream.write(
            f"""
    <tr class="trophy-{'obtained' if trophy.obtained else 'unobtained'}">
        <td width="7%" style="text-align: center;">
                    <img src="{trophy.img_source}" width="70%">
                </td>
                <td width="75%">
                    <p>
                        <b>{trophy.name}</b><br />
                        <i>{trophy.description}</i>{details}
                    </p>
                </td>
                <td width="15%" style="text-align: center;">
                    {obtained}
                </td>
                <td width="3%">
                    <img src="../trophies/40-{trophy.level.name.lower()}.png" width="90%">
                </td>
            </tr>
""")

    stream.write("</table>")


def main():
    for game in get_game_data(DBFILENAME):
        stream = io.StringIO()

        write_header(stream, game)
        write_trophies(stream, game["trophies"])
        stream.write('''</div>

    <div style="padding-top: 100px;">
    </div>

</body>

</html>''')

        with open(HERE.parent / game["FolderName"] / "trophies.html", "w+") as f:
            stream.seek(0)
            f.write(stream.read())


if __name__ == "__main__":
    main()
