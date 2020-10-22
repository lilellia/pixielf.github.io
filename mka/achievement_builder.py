import csv
import io
import pathlib


def write(trophy: dict, stream: io.StringIO) -> None:
    # set up row
    tr_class = 'obtained' if trophy.get('Obtained') else 'unobtained'
    stream.write(f'<tr class="trophy-{tr_class}">\n')

    # image column
    img_src = trophy.get('Image', '')
    stream.write(f'''\
    <td width="7%" style="text-align: center;">
        <img src="{img_src}" width="70%">
    </td>''')

    # trophy text
    trophy_name = trophy.get('Name', '')
    description = trophy.get('Description', '')
    detail = trophy.get('Detail', '')

    stream.write('<td width="75%">\n')
    stream.write('<p>\n')
    stream.write(f'<b>{trophy_name}</b><br/>\n')
    stream.write(f'<i>{description}</i>\n')
    if detail:
        stream.write(f'<br/><span class="detail">{detail}</span>')
    stream.write('</p>')
    stream.write('</td>')

    # obtained column
    obtained = trophy.get('Obtained', '')
    stream.write(f'''
    <td width="15%" style="text-align: center;">
        {obtained}
    </td>''')

    # trophy level
    level = trophy.get('Level', '').lower()
    stream.write(f'''
    <td width="3%">
        <img src="imgs/40-{level}.png" width="90%">
    </td>
    ''')

    stream.write('\n</tr>')


def format_level(counts: dict, level: str):
    obtained, total = counts[level]
    return f'{obtained}/{total}'


here = pathlib.Path(__file__).resolve().parent
datafile = here / 'raw_data' / 'achievements.csv'

stream = io.StringIO()
counts = {'bronze': [0, 0], 'silver': [0, 0], 'gold': [0, 0], 'platinum': [0, 0]}

with open(datafile, 'r') as f:
    reader = csv.DictReader(f)

    for trophy in reader:
        # write trophy HTML to stream
        write(trophy, stream)

        # update counts
        level = trophy.get('Level', '').lower()
        counts[level][0] += bool(trophy.get('Obtained'))
        counts[level][1] += 1


with open(here / 'achievements.html', 'w') as f:
    obtained = sum(x for k, (x, y) in counts.items())
    total = sum(y for k, (x, y) in counts.items())
    icon = 'on' if obtained == total else 'off'
    f.write(f'''<html>

<head>
    <title>
        Mana Khemia Achievements
    </title>
    <link href="https://fonts.googleapis.com/css?family=Tangerine" rel="stylesheet" />
    <link href="https://fonts.googleapis.com/css?family=Montserrat" rel="stylesheet" />
    <link href="../mka/style.css" rel="stylesheet" />
    <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
    <link rel="icon" href="../favicon.png" type="image/x-icon">
</head>

<body style="font-family: Montserrat, sans-serif;">
    <div>
        <!-- header -->
        <table class="zebra">
            <tr>
                <td width="10%" style="text-align: center;"><img src="imgs/mklogo.png" width="95%"></td>
                <td width="75%"><b style="font-size: 200%;">Mana Khemia: Alchemists of Al-Revis</b></td>
                <td width="3%"><img src="imgs/complete-icon-{icon}.png"></td>
                <td width="13%;">{obtained}/{total} trophies obtained</td>
            </tr>
            <tr>
                <td></td>
                <td>
                    <img src="imgs/40-platinum.png"> {format_level(counts, "platinum")}
                    <img src="imgs/40-gold.png"> {format_level(counts, "gold")}
                    <img src="imgs/40-silver.png"> {format_level(counts, "silver")}
                    <img src="imgs/40-bronze.png"> {format_level(counts, "bronze")}
                </td>
            </tr>
        </table>

        <table class="zebra">''')

    stream.seek(0)
    f.write(stream.read())

    f.write('''</table>
    </div>

    <div style="padding-top: 100px;">
        <p style="font-size: 70%;">Achievement images taken from the <a
                href="https://atelier.fandom.com/wiki/Atelier_Wiki">Atelier Wiki</a>, used under the Creative Commons
            Attribution-Share Alike License 3.0 (Unported) (CC-BY-SA).</p>
    </div>

</body>

</html>''')
