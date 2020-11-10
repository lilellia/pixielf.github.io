# flake8: noqa E501

import re


def darkness(html: str):
    """ "Darkness's Voice from the Abyss" has alternate endings that are handled by a separate JS script.
    This function intercepts the htmlification and appends the necessary HTML/JS to accompany it.
    """
    necessary = """\
<table style="width: 100%;">
    <tr>
        <td style="width: 3%; border: none;">
            <img src="../mka/imgs/philo.png" width="90%;" onmouseover="changeEnding('philo')" onmouseout="changeEnding(null)"><br/>
            <img src="../mka/imgs/nikki.png" width="90%;" onmouseover="changeEnding('nikki')" onmouseout="changeEnding(null)"><br/>
            <img src="../mka/imgs/pamela.png" width="90%;" onmouseover="changeEnding('pamela')" onmouseout="changeEnding(null)"><br/>
            <img src="../mka/imgs/flay.png" width="90%;" onmouseover="changeEnding('flay')" onmouseout="changeEnding(null)"><br/>
            <img src="../mka/imgs/roxis.png" width="90%;" onmouseover="changeEnding('roxis')" onmouseout="changeEnding(null)"><br/>
            <img src="../mka/imgs/anna.png" width="90%;" onmouseover="changeEnding('anna')" onmouseout="changeEnding(null)"><br/>
            <img src="../mka/imgs/muppy.png" width="90%;" onmouseover="changeEnding('muppy')" onmouseout="changeEnding(null)"><br/>
        </td>
        <td id="endingSwitch" style="width: 94%; border: none;"></td>
    </tr>
</table>

<script type="text/javascript">
    let endings = {
        "philo": [
            "But it was a softer voice",
            "That made its way to me—",
            "A whistling girl who learned too well",
            "The pain she'd leave for me.",
            "Reminders of my promise made",
            "And cries of futures lost,",
            "I learned to chase our happiness,",
            "Gave up my powers as the cost."
        ],

        "nikki": [
            "And just as quick, I feel myself",
            "Pulled away from the edge.",
            "A promise made and yet unkept,",
            "I'd be dragged to meet that pledge.",
            "I never could doubt her resolve,",
            "And I can't give up my life,",
            "For us to have our happiness,",
            "I must make her my wife."
        ],

        "pamela": [
            "A tearful cry is the response—",
            "I can't help but smile in return.",
            "For even through her common tricks,",
            "I can feel her real concern.",
            "And what an irony it is",
            "To have such a savior ghost.",
            "But if there's someone I can't let cry,",
            "Then it's her, foremost."
        ],

        "flay": [
            "But it's a stronger laugh that calls me back",
            "With its worldview black and white—",
            "Or red, perhaps, of copper hue,",
            "Ready to stand and fight.",
            "And with that, a hero saved,",
            "Laughing back with equal weight—",
            "For, perhaps, it's not so hard",
            "To force this darkness to abate."
        ],

        "roxis": [
            "A brutal tirade, a hateful rant",
            "Comes from behind me, from the light.",
            "A truly twisted argument,",
            "But I can't deny it's right.",
            "But just the same, I can't allow",
            "This to be my legacy.",
            "I know it's foolish, too small, perhaps,",
            "But I can't give in to your jealousy."
        ],

        "anna": [
            "A smaller voice of quiet strength",
            "Brings forth a solution:",
            "Instead of selfish, rash action,",
            "We should clear my confusion.",
            "Her own selfishness, in its own way,",
            "Is perhaps the greatest cure—",
            "For how could I deny that wish",
            "That belongs not just to her?"
        ],

        "muppy": [
            "At first, there's not but a tense silence",
            "Where I don't know what to say.",
            "Then suddenly, a bright, warm light",
            "That makes the darkness go away.",
            "Two as one, a heartbeat felt,",
            "Shared between two beings strange—",
            "But if this hope is really true,",
            "Then I can learn to change."
        ]
    };

    function changeEnding(charName) {
        let el = document.getElementById('endingSwitch');

        if (charName === null) {
            el.innerHTML = "";
            return;
        }

        let rows = endings[charName];

        let html = "<p>\\n";
        for(let i = 0; i < 4; i++) {
            html += rows[i] + "<br/>\\n";
        }
        html += "</p>\\n<p>\\n";

        for(let j = 4; j < 8; j++) {
            html += rows[j] + "<br/>\\n";
        }
        html += "</p>";

        el.innerHTML = html;
    }
</script>
"""

    return html + '\n' + necessary


def one(html):
    """ "One" creates level-2 headers to separate its two parts. The default htmlifier inserts those within
    a <p> tag. This function pulls that back out.
    """
    return re.sub(r'<p>\s*<h2(.*)/h2>\s*</p>', '<h2\g<1>/h2>', html, re.MULTILINE)  # noqa W605


HELPERS = {
    "Darkness's Voice from the Abyss": darkness,
    "One": one
}
