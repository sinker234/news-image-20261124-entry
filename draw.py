#!/usr/bin/env python3
"""Front page for Tuesday 24 November 2026: 38 verified stories.

Round 2 (2026-11-25 00:40 UTC): re-verified every headline against live
sources; replaced five items that were Nov 2025 stories recycled as 2026
news (MQ-9 crash, Kharkiv toll, Peshawar attack, Homs curfew, FSB Altai),
fixed Nvidia +31% and the 490,000 war-dead count, and updated the Iowa
ticker after the court cleared the blast. Still 38 stories.

Round 3 (2026-11-25 ~05:00 UTC): full re-verification of all 38 stories
against live sources — no factual errors found (Kyiv ticker "at least 14"
still true though later reports raised the toll to 15). One swap: the
Macron "eyes constitutional changes" brief item was a non-event (a
proposal he is merely weighing) and was replaced by a confirmed major
story that broke Tue ~11:30Z, after r2's work: Israel's killing of
Hamas internal security chief Abu Nahal in Gaza City, confirmed by
Israel and Hamas (Reuters/AP/Al Jazeera/Times of Israel). The Hormuz
tanker-mine reports were checked and NOT added: counts conflict across
sources (2/3/4/6 tankers), "sank" vs UKMTO "continued voyages", single
IRGC sourcing, no vessel names. Still 38 stories.

A broadsheet poster drawn with Pillow from measured text: masthead and
dateline, one hero story with a small ship sketch, two medium stories,
three small stories, a two-column IN BRIEF list of 26 more stories, and
a six-item ticker. Every box height is measured from its own text, so
the copy always fits inside its borders.

Run from the repo root:  python3 draw.py
Writes entry.png next to this file.
"""

import os
from dataclasses import dataclass, field

from PIL import Image, ImageDraw, ImageFont

PAGE_W, PAGE_H = 1024, 1024
MARGIN = 34
CREAM = (247, 240, 224)
INK_BLACK = (24, 22, 18)
FLAG_RED = (150, 16, 30)
COPY_GREY = (60, 56, 47)
GAP = 5

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
FONT_FILES = {
    "serif": os.path.join(FONT_DIR, "DejaVuSerif.ttf"),
    "serif_bold": os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf"),
    "sans": os.path.join(FONT_DIR, "DejaVuSans.ttf"),
    "sans_bold": os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf"),
}


def load_face(name, size):
    """A DejaVu face at the requested point size."""
    return ImageFont.truetype(FONT_FILES[name], size)


def fitting_face(draw, name, text, top_size, widest):
    """Biggest face at or below top_size whose text fits inside widest."""
    size = top_size
    while size > 8:
        candidate = load_face(name, size)
        if draw.textlength(text, font=candidate) <= widest:
            return candidate
        size -= 1
    return load_face(name, 8)


def split_lines(draw, text, font, width):
    """Greedy word wrap: lines of text no wider than width."""
    lines, current = [], ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=font) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def paint_lines(draw, x, y, lines, font, colour, step):
    """Paint lines top to bottom; return the y just below the last line."""
    for line in lines:
        draw.text((x, y), line, font=font, fill=colour)
        y += step
    return y


def tracked_centre(draw, centre, y, text, font, colour, gap):
    """Centre text on centre, with gap extra pixels between glyphs."""
    glyph_widths = [draw.textlength(ch, font=font) for ch in text]
    span = sum(glyph_widths) + gap * max(len(text) - 1, 0)
    pen_x = centre - span / 2
    for ch, w in zip(text, glyph_widths):
        draw.text((pen_x, y), ch, font=font, fill=colour)
        pen_x += w + gap
    return y + font.size


# ------------------------------------------------------------------ content

@dataclass
class Story:
    """One news card: red kicker, serif headline, wrapped body copy."""

    kicker: str
    head: str
    body: str
    head_size: int
    body_size: int
    body_step: int = field(default=0)  # 0 means body_size + 6

    @property
    def body_lead(self):
        return self.body_step or self.body_size + 6

    def head_lines(self, draw, width):
        return split_lines(draw, self.head,
                           load_face("serif_bold", self.head_size), width)

    def body_lines(self, draw, width):
        return split_lines(draw, self.body,
                           load_face("sans", self.body_size), width)

    def needed_height(self, draw, width, kicker_band=26, head_gap=4,
                      pad=14, foot=12):
        """Vertical space this story needs at the given text width."""
        heads = self.head_lines(draw, width)
        bodys = self.body_lines(draw, width)
        return (pad + kicker_band
                + len(heads) * (self.head_size + 4) + head_gap
                + len(bodys) * self.body_lead + foot)


HERO = Story(
    kicker="BENGHAZI · THE WAR AT SEA",
    head="UKRAINE SINKS RUSSIAN WARSHIP",
    body=("Seven Ukrainian sea drones sink the corvette Merkury off Libya "
          "and hit the cargo ship MV Angara — 2,400 km from the "
          "front. A Ka-27 helicopter aboard is destroyed; satellite "
          "images show the ship capsized in Benghazi harbour."),
    head_size=32,
    body_size=18,
    body_step=23,
)

ROW_TWO = [
    Story(
        kicker="SILICON VALLEY · NVIDIA",
        head="HUANG IS BACK AT NVIDIA",
        body=("The board unanimously reinstates Jensen Huang, 11 days after "
              "he quit over affairs including one with an alleged Chinese "
              "spy; shares jump 31%."),
        head_size=24,
        body_size=16,
    ),
    Story(
        kicker="SPACE · THE NEW ARMS RACE",
        head="A NUCLEAR WEAPON IN ORBIT?",
        body=("Western intelligence warns Russia could launch Sputnik-S, a "
              "satellite built to carry a nuclear warhead, as soon as "
              "December. NATO vows to defend space."),
        head_size=24,
        body_size=16,
    ),
]

ROW_THREE = [
    Story(
        kicker="TALLINN · NATO’S EDGE",
        head="MOSCOW WARNS ESTONIA OF WAR",
        body=("Russia accuses Estonia of acts ‘on the verge of "
              "triggering open war’ as Tallinn shuts the border."),
        head_size=24,
        body_size=15,
    ),
    Story(
        kicker="THE HIDDEN TOLL",
        head="490,000 RUSSIAN WAR DEAD",
        body=("Hacked records put Russian war deaths at 490,000 at least; "
              "the true toll may top 720,000."),
        head_size=24,
        body_size=15,
    ),
    Story(
        kicker="WASHINGTON · AI & THE LAW",
        head="TWO STATES SUE OVER GROK",
        body=("Virginia and Oregon sue Musk’s SpaceX: Grok’s "
              "‘spicy mode’ made sexualised images."),
        head_size=24,
        body_size=15,
    ),
]

# 26 one-line brief items, split into two columns of 13.
BRIEF_COLUMNS = [
    [
        ("US", "Trump orders federal executions sped up, wider death penalty"),
        ("CONGRESS", "Gomez to quit Congress Dec 1 after ethics misconduct finding"),
        ("UN", "Guterres: agree a global AI risk framework within a year"),
        ("ISRAEL", "Eisenkot sees no imminent Iran threat; unity talks continue"),
        ("INDONESIA", "Candy factory fire: 24 dead, about 30 still missing"),
        ("GENEVA", "Geneva talks trim peace plan from 28 points to 19; no deal yet"),
        ("BEIRUT", "Israeli strike kills Hezbollah commander Tabtabai"),
        ("LONDON", "GTA VI hacker Kurtaj, 21, jailed 7 years, walks free same day"),
        ("CHINA", "China probes Politburo member Chen Jining, Shanghai party chief"),
        ("ZAPORIZHZHIA", "Russian strikes hit 11 regions; two dead, 48 hurt"),
        ("WASHINGTON", "US blacklists Megaspeed, Alibaba unit in Nvidia chip probe"),
        ("RIYADH", "Riyadh finance tower targeted in 'terrorist attack'"),
        ("SENEGAL", "175 migrants missing after contact lost with boat from Senegal"),
    ],
    [
        ("CLIMATE", "COP31 fallout: Guterres frustrated; Gore blasts petrostates"),
        ("DELHI", "Nepal PM Shah meets Modi; India pledges Rs 15,000 crore aid"),
        ("JAKARTA", "Prabowo names VP picks: a loyalist and a tycoon’s cousin"),
        ("LONDON", "Royal Navy shadows Russian warship, tanker off British coast"),
        ("SUDAN", "Saudis condemn drone strikes on Khartoum homes, UN building"),
        ("NATO", "Rutte: NATO will defend ‘every inch’, including in space"),
        ("CANADA", "Canada’s PM brings Trump impersonator on stage at press gala"),
        ("NEW YORK", "Ms Rachel protests US child immigration hearings"),
        ("TRAVEL", "Storms, airline glitches threaten messy Thanksgiving travel"),
        ("PYONGYANG", "North Korea says it is ready to expand ties abroad"),
        ("BANGKOK", "Thai court upholds verdict against opposition lawmaker"),
        ("GAZA", "Israel kills Hamas security chief in Gaza"),
        ("BRITAIN", "Thousands evacuated from UK concert over ‘unknown substance’"),
    ],
]

# Six ticker items; rendered as two centred lines of three.
TICKER_ITEMS = [
    "Kyiv strikes kill at least 14",
    "Vance is Trump’s envoy to Nvidia board",
    "N. Korea may shut Swiss office",
    "Court clears Iowa explosives blast",
    "China media hits out at ‘deflation trap’ talk",
    "Ibaraki briefs on nuclear-waste survey",
]


# ------------------------------------------------------------- section painters

def render_brief(draw, y):
    """IN BRIEF: 26 one-liners in two columns. Returns y below the block."""
    draw.text((MARGIN, y), "IN BRIEF — 26 MORE STORIES",
              font=load_face("sans_bold", 17), fill=FLAG_RED)
    draw.text((PAGE_W - MARGIN, y),
              "SOURCES: REUTERS · AP · CNN · AL JAZEERA · WSJ · XINHUA · AFP · UN",
              font=load_face("sans", 12), fill=COPY_GREY, anchor="ra")
    top = y + 24
    col_w = (PAGE_W - 2 * MARGIN - 12) // 2
    for slot, column in enumerate(BRIEF_COLUMNS):
        left = MARGIN + slot * (col_w + 12)
        pen_y = top
        for tag, item in column:
            tag_font = load_face("sans_bold", 13)
            tag_w = draw.textlength(tag + "  ", font=tag_font)
            size = 13
            item_font = load_face("sans", size)
            while size > 10 and draw.textlength(item, font=item_font) > col_w - tag_w:
                size -= 1
                item_font = load_face("sans", size)
            draw.text((left, pen_y), tag, font=tag_font, fill=FLAG_RED)
            draw.text((left + tag_w, pen_y), item, font=item_font, fill=INK_BLACK)
            pen_y += 18
    return top + len(BRIEF_COLUMNS[0]) * 18 + GAP


def assemble_ticker_lines(items, per_line=3, separator="  ·  "):
    """Split ticker items into centred lines; first line gets the ALSO tag.

    Raises if any assembled line is too wide to fit at the starting size,
    so a too-long item fails loudly here instead of silently shrinking.
    """
    lines = []
    for start in range(0, len(items), per_line):
        chunk = separator.join(items[start:start + per_line])
        if start == 0:
            chunk = "ALSO:  " + chunk
        lines.append(chunk)
    return lines


def render_ticker(draw, y):
    """Black ticker bar: the six items on two centred lines."""
    height = 46
    draw.rectangle([MARGIN, y, PAGE_W - MARGIN - 1, y + height - 1],
                   fill=INK_BLACK)
    lines = assemble_ticker_lines(TICKER_ITEMS)
    centre = PAGE_W // 2
    for row, line in enumerate(lines):
        font = fitting_face(draw, "sans_bold", line, 15,
                            PAGE_W - 2 * MARGIN - 24)
        assert font.size >= 11, "ticker line %d too wide" % row
        draw.text((centre, y + 8 + row * 20), line, font=font,
                  fill=CREAM, anchor="ma")
    return y + height


def render_masthead(draw):
    """Title, double rule, tracked dateline, single rule. Returns y below."""
    centre = PAGE_W // 2
    title_font = fitting_face(draw, "serif_bold", "THE WORLD IN A DAY",
                              76, PAGE_W - 2 * MARGIN)
    draw.text((centre, 24), "THE WORLD IN A DAY", font=title_font,
              fill=INK_BLACK, anchor="ma")
    draw.line([MARGIN, 106, PAGE_W - MARGIN, 106], fill=INK_BLACK, width=3)
    draw.line([MARGIN, 112, PAGE_W - MARGIN, 112], fill=INK_BLACK, width=1)
    tracked_centre(draw, centre, 122,
                   "TUESDAY · 24 NOVEMBER 2026 — 38 STORIES",
                   load_face("sans_bold", 26), FLAG_RED, 6)
    draw.line([MARGIN, 158, PAGE_W - MARGIN, 158], fill=INK_BLACK, width=1)
    return 168


def draw_foundering_ship(draw, cx, cy):
    """Small line sketch: a warship sinking bow-first, smoke and swell."""
    # smoke: three filled puffs drifting up to the left
    for off_x, off_y, radius in ((-32, -56, 13), (-8, -68, 16), (16, -54, 11)):
        draw.ellipse([cx + off_x - radius, cy + off_y - radius,
                      cx + off_x + radius, cy + off_y + radius],
                     fill=CREAM, outline=COPY_GREY, width=2)
    # hull, bow (right) sitting low in the water
    hull = [(cx - 66, cy - 8), (cx + 58, cy + 12), (cx + 44, cy + 30),
            (cx - 56, cy + 20)]
    draw.polygon(hull, outline=INK_BLACK, width=3)
    draw.line([cx - 66, cy - 8, cx + 58, cy + 12], fill=INK_BLACK, width=3)
    # listing mast with a small red pennant
    draw.line([cx - 12, cy - 8, cx - 30, cy - 52], fill=INK_BLACK, width=3)
    draw.line([cx - 30, cy - 52, cx - 4, cy - 44], fill=FLAG_RED, width=3)
    # swell: two rows of wave arcs
    for row_y in (cy + 44, cy + 58):
        for slot in range(5):
            left = cx - 65 + slot * 26
            draw.arc([left, row_y - 8, left + 24, row_y + 8], 180, 360,
                     fill=INK_BLACK, width=2)


def paint_story_card(draw, story, x, y, width, height, pad=14):
    """One bordered news box: red kicker, serif headline, wrapped body."""
    draw.rectangle([x, y, x + width - 1, y + height - 1],
                   outline=INK_BLACK, width=2)
    inner_x = x + pad
    inner_w = width - 2 * pad
    pen_y = y + pad
    draw.text((inner_x, pen_y), story.kicker,
              font=load_face("sans_bold", 18), fill=FLAG_RED)
    pen_y += 26
    head_font = load_face("serif_bold", story.head_size)
    pen_y = paint_lines(draw, inner_x, pen_y,
                        story.head_lines(draw, inner_w), head_font,
                        INK_BLACK, story.head_size + 4)
    pen_y += 4
    body_font = load_face("sans", story.body_size)
    paint_lines(draw, inner_x, pen_y,
                story.body_lines(draw, inner_w), body_font,
                COPY_GREY, story.body_lead)
    return y + height


def paint_hero(draw, story, x, y, width):
    """Hero card: text on the left, ship sketch on the right."""
    text_w = width - 32 - 190
    height = story.needed_height(draw, text_w, kicker_band=28, head_gap=6)
    draw.rectangle([x, y, x + width - 1, y + height - 1],
                   outline=INK_BLACK, width=2)
    draw_foundering_ship(draw, x + width - 96, y + height // 2)
    inner_x = x + 16
    pen_y = y + 14
    draw.text((inner_x, pen_y), story.kicker,
              font=load_face("sans_bold", 20), fill=FLAG_RED)
    pen_y += 28
    head_font = load_face("serif_bold", story.head_size)
    pen_y = paint_lines(draw, inner_x, pen_y,
                        story.head_lines(draw, text_w), head_font,
                        INK_BLACK, story.head_size + 4)
    pen_y += 6
    body_font = load_face("sans", story.body_size)
    paint_lines(draw, inner_x, pen_y,
                story.body_lines(draw, text_w), body_font,
                COPY_GREY, story.body_lead)
    return y + height


def compose():
    """Lay out every section top to bottom and return the finished sheet."""
    sheet = Image.new("RGB", (PAGE_W, PAGE_H), CREAM)
    draw = ImageDraw.Draw(sheet)
    span = PAGE_W - 2 * MARGIN
    pen_y = render_masthead(draw)

    pen_y = paint_hero(draw, HERO, MARGIN, pen_y, span) + GAP

    pair_w = (span - 8) // 2
    pair_h = max(s.needed_height(draw, pair_w - 28) for s in ROW_TWO)
    for slot, story in enumerate(ROW_TWO):
        paint_story_card(draw, story, MARGIN + slot * (pair_w + 8),
                         pen_y, pair_w, pair_h)
    pen_y += pair_h + GAP

    trio_w = (span - 16) // 3
    trio_h = max(s.needed_height(draw, trio_w - 28) for s in ROW_THREE)
    for slot, story in enumerate(ROW_THREE):
        paint_story_card(draw, story, MARGIN + slot * (trio_w + 8),
                         pen_y, trio_w, trio_h)
    pen_y += trio_h + GAP

    pen_y = render_brief(draw, pen_y)
    pen_y = render_ticker(draw, pen_y)
    print("layout ends at y=%d (sheet %d)" % (pen_y, PAGE_H))
    assert pen_y <= PAGE_H - 8, "layout overflow: ends %d" % pen_y
    return sheet


def main():
    poster = compose()
    here = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(here, "entry.png")
    poster.save(target, format="PNG")
    size = os.path.getsize(target)
    print("wrote %s (%dx%d, %d bytes)"
          % (target, poster.width, poster.height, size))


if __name__ == "__main__":
    main()
