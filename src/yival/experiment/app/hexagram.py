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
}, {
    "name":
    "夬 (Guài)",
    "description":
    "Displacement",
    "figure":
    "兌乾",
    "reading":
    "The situation may have been stagnant for a while, but now is the moment for breakthroughs."
}, {
    "name":
    "大有 (Dà Yǒu)",
    "description":
    "A time of great prosperity and success",
    "figure":
    "離乾",
    "reading":
    "The situation may have been stagnant for a while, but now is the moment for breakthroughs."
}, {
    "name":
    "大壮 (Dà Zhuàng)",
    "description":
    "Demonstrating power and strength without resorting to force.",
    "figure":
    "兌乾",
    "reading":
    "Harness your inner strength and potential. Approach challenges with confidence but avoid unnecessary aggression."
}, {
    "name":
    "小畜 (Xiǎo Xù) ",
    "description":
    "Cultivating and nourishing incremental growth.",
    "figure":
    "巽乾",
    "reading":
    "Focus on nurturing small endeavors or projects. Gentle and steady progress will yield benefits."
}, {
    "name":
    "需 (Xū)",
    "description":
    "A period of waiting for the right moment to act.",
    "figure":
    "坎乾",
    "reading":
    "Patience is required. Wait for the right moment to act, and avoid making hasty decisions."
}, {
    "name":
    "大畜 (Dà Chù)",
    "description":
    "Accumulating resources and energy for future endeavors.",
    "figure":
    "艮乾",
    "reading":
    "Now is a time to gather strength and resources. Prepare wisely for the future."
}, {
    "name":
    "泰 (Tài)",
    "description":
    "Harmony, balance, and a favorable turn of events.",
    "figure":
    "坤乾",
    "reading":
    "This is a time of peace and prosperity. Both the inner and outer aspects of life are in harmony. Make the most of this auspicious period by promoting unity and understanding."
}, {
    "name":
    "否 (Pǐ)",
    "description":
    "A period of obstruction and difficulty.",
    "figure":
    "乾坤",
    "reading":
    "Progress may be blocked, but patience and perseverance will be required. Internal reflection can provide clarity during this stagnant period."
}, {
    "name":
    "萃 (Cuì)",
    "description":
    " Accumulation and convergence of forces.",
    "figure":
    "兌坤",
    "reading":
    "A time of gathering and coming together. Unity and collaboration will lead to success."
}, {
    "name":
    "晋 (Jìn) ",
    "description":
    "Inspiration, delight, and excitement.",
    "figure":
    "離坤",
    "reading":
    "Conditions are favorable for progress. Seize opportunities and move forward with confidence"
}, {
    "name":
    "豫 (Yù)",
    "description":
    "Harmony, balance, and a favorable turn of events.",
    "figure":
    "震坤",
    "reading":
    "Harness the energy and enthusiasm of this period. Celebrate joys and share your excitement with others"
}, {
    "name":
    "觀 (Guàn)",
    "description":
    "Observation, reflection, and insight.",
    "figure":
    "巽坤",
    "reading":
    "This is a time of peace and prosperity. Both the inner and outer aspects of life are in harmony. Make the most of this auspicious period by promoting unity and understanding."
}, {
    "name":
    "比 (Bǐ)",
    "description":
    "Unity, partnership, and mutual support.",
    "figure":
    "坎坤",
    "reading":
    "Strengthen bonds and alliances. Mutual support and cooperation lead to success."
}, {
    "name":
    "剥 (Bō)",
    "description":
    "Decline, deterioration, and separation.",
    "figure":
    "艮坤",
    "reading":
    "External challenges may lead to breakdowns. Stay resilient and prepare for potential setbacks."
}, {
    "name":
    "履 (Lǚ)",
    "description":
    "Treading or Conduct. Walking the correct path and understanding the impact of one's behavior.",
    "figure":
    "乾兌",
    "reading":
    "Your behavior and decisions shape your journey. Choose your steps wisely."
}, {
    "name":
    "睽 (Kuí)",
    "description":
    "Opposition or Conflict. Understanding contrasts and finding complementarity in differences.",
    "figure":
    "離兌",
    "reading":
    "Embrace differences and seek harmony amidst contrasts."
}, {
    "name":
    "歸妹 (Guīmèi)",
    "description":
    "Marrying Maiden. Embracing union and understanding the adjustments of partnerships.",
    "figure":
    "震兌",
    "reading":
    "Partnerships bring challenges. Adapt and grow together."
}, {
    "name":
    "中孚 (Zhōngfú)",
    "description":
    "Inner Truth or Integrity. The importance of sincerity and staying true to oneself.",
    "figure":
    "巽兌",
    "reading":
    "Integrity leads to success. Stay true to your inner self."
}, {
    "name": "節 (Jié)",
    "description":
    "Limitation or Restraint. The value of moderation and setting boundaries.",
    "figure": "坎兌",
    "reading": "Set limits and know when to exercise restraint."
}, {
    "name": "損 (Sǔn)",
    "description":
    "Decrease or Loss. Recognizing the need to let go for a greater purpose.",
    "figure": "艮兌",
    "reading": "Sometimes, letting go leads to greater gains."
}, {
    "name": "臨 (Lín)",
    "description":
    "Approach. Understanding the best way to tackle situations or challenges.",
    "figure": "坤兌",
    "reading": "Approach challenges with wisdom and clarity."
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
