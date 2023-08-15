
from dash import html  # type: ignore

TRIGRAMS = {
    "乾": ["yang", "yang", "yang"],
    "坤": ["yin", "yin", "yin"],
    "震": ["yin", "yin", "yang"],
    "巽": ["yang", "yang", "yin"],
    "坎": ["yin", "yang", "yin"],
    "離": ["yang", "yin", "yang"],
    "艮": ["yang", "yin", "yin"],
    "兌": ["yin", "yang", "yang"]
}

# Sample Data
HEXAGRAMS = [{
    "name":
    "乾 (Qián)",
    "description":
    "The Creative",
    "figure":
    "乾乾",
    "reading":
    "Represents the power of the great. It's a time of strength and initiative, a favorable period for beginnings."
}, {
    "name":
    "坤 (Kūn)",
    "description":
    "The Receptive",
    "figure":
    "坤坤",
    "reading":
    "Symbolizes receptivity and adaptability. It's a time to be open to guidance and to yield for achieving goals."
}, {
    "name":
    "震 (Zhèn)",
    "description":
    "The Arousing",
    "figure":
    "震震",
    "reading":
    "Symbolizes activity and excitement. It's a time of movement and change, urging one to take action."
}, {
    "name":
    "巽 (Xùn)",
    "description":
    "The Gentle",
    "figure":
    "巽巽",
    "reading":
    "Represents gentleness and adaptability. It's a period to be flexible and persuasive rather than forceful."
}, {
    "name":
    "坎 (Kǎn)",
    "description":
    "The Abysmal",
    "figure":
    "坎坎",
    "reading":
    "Indicates danger and challenges. It's a time to be cautious and to seek guidance before proceeding."
}, {
    "name":
    "離 (Lí)",
    "description":
    "The Clinging",
    "figure":
    "離離",
    "reading":
    "Indicates light and clarity. It's a period of illumination, understanding, and clarity."
}, {
    "name":
    "艮 (Gèn)",
    "description":
    "Keeping Still",
    "figure":
    "艮艮",
    "reading":
    "Represents stillness and immovability. It's a time for reflection, meditation, and grounding."
}, {
    "name":
    "兌 (Duì)",
    "description":
    "The Joyous",
    "figure":
    "兌兌",
    "reading":
    "Signifies joy and satisfaction. It's a period of pleasure, communication, and openness."
}]

def generate_hexagram_figure(figure):

    lines = []
    for char in figure:
        for line in TRIGRAMS[char]:
            if line == "yang":
                lines.append(html.Div(className="yang-line"))
            else:
                lines.append(
                    html.Div([
                        html.Div(className="yin-line-part"),
                        html.Div(className="yin-line-part")
                    ],
                                className="yin-line")
                )

    return html.Div(lines, className="hexagram")
