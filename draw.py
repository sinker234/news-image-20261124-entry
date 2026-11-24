#!/usr/bin/env python3
"""Render the front page for Tuesday 24 November 2026.

A single broadsheet poster drawn entirely with Pillow: masthead, dateline,
one hero story, five smaller stories, a two-column IN BRIEF list of 26 more
verified stories, and a news ticker -- 38 stories in all. Every box is
sized from its measured text, so nothing ever overflows.
Run it from the repo root; it writes ``entry.png`` next to this file.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- palette
SHEET_W = 1024
SHEET_H = 1024
EDGE = 34                      # outer margin on both sides
PAPER = (247, 240, 224)        # warm newsprint cream
INK = (24, 22, 18)             # near-black type
CRIMSON = (150, 16, 30)        # kicker / dateline red
BODY_GREY = (60, 56, 47)       # body copy

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SERIF_BOLD = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")


def face(path, size):
    """Load a truetype face at the requested point size."""
    return ImageFont.truetype(path, size)


def shrink_to_fit(path, text, start_size, max_width):
    """Largest size at or below ``start_size`` that fits ``max_width``."""
    probe = Image.new("RGB", (8, 8))
    ruler = ImageDraw.Draw(probe)
    size = start_size
    while size > 8:
        font = face(path, size)
        if ruler.textlength(text, font=font) <= max_width:
            return font
        size -= 1
    return face(path, 8)


def wrap_text(ruler, text, font, width):
    """Greedy word wrap; returns a list of lines that fit ``width``."""
    lines = []
    current = ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if ruler.textlength(trial, font=font) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_lines(ruler, x, y, lines, font, fill, leading):
    """Draw stacked lines; return the y coordinate just past the last one."""
    for line in lines:
        ruler.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def spaced_line(ruler, centre_x, y, text, font, fill, tracking):
    """Draw ``text`` centred on ``centre_x`` with extra space per glyph."""
    widths = [ruler.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * max(len(text) - 1, 0)
    cursor = centre_x - total / 2
    for ch, w in zip(text, widths):
        ruler.text((cursor, y), ch, font=font, fill=fill)
        cursor += w + tracking
    return y + font.size


def paint_sinking_ship(ruler, cx, cy):
    """A warship going down by the bow, smoke rising, waves below."""
    # smoke puffs
    for dx, dy, r in ((-28, -52, 14), (-8, -64, 17), (14, -50, 12)):
        ruler.ellipse([cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r],
                      outline=BODY_GREY, width=2)
    # hull, tilted down at the bow (right side low)
    hull = [(cx - 62, cy - 6), (cx + 58, cy + 14), (cx + 44, cy + 30),
            (cx - 52, cy + 22)]
    ruler.polygon(hull, outline=INK, width=3)
    ruler.line([cx - 62, cy - 6, cx + 58, cy + 14], fill=INK, width=3)
    # mast, leaning with the list
    ruler.line([cx - 8, cy - 8, cx - 22, cy - 46], fill=INK, width=3)
    ruler.line([cx - 22, cy - 46, cx + 2, cy - 40], fill=CRIMSON, width=3)
    # waves
    for wy in (cy + 44, cy + 58):
        for k in range(-2, 3):
            x0 = cx + k * 30 - 12
            ruler.arc([x0, wy - 8, x0 + 24, wy + 8], 180, 360,
                      fill=INK, width=2)


def measure_story(ruler, headline, body, head_px, body_px, inner_w):
    """Line counts for a story at the given sizes; used to size its box."""
    head_lines = wrap_text(ruler, headline, face(SERIF_BOLD, head_px),
                           inner_w)
    body_lines = wrap_text(ruler, body, face(SANS, body_px), inner_w)
    return len(head_lines), len(body_lines)


def box_height(head_line_count, body_line_count, head_px, body_px,
               pad=14, bottom_pad=12):
    """Vertical space a story box needs for its measured lines."""
    return (pad + 26
            + head_line_count * (head_px + 4) + 4
            + body_line_count * (body_px + 6) + bottom_pad)


def story_box(ruler, x, y, w, h, kicker, headline, body,
              head_px, body_px, pad=14):
    """One bordered news box: red kicker, serif headline, wrapped body.

    ``h`` must be at least ``box_height(...)`` for the same text, so the
    copy always ends above the bottom border.
    """
    ruler.rectangle([x, y, x + w - 1, y + h - 1], outline=INK, width=2)
    inner_x = x + pad
    inner_w = w - 2 * pad
    cursor = y + pad
    ruler.text((inner_x, cursor), kicker,
               font=face(SANS_BOLD, 18), fill=CRIMSON)
    cursor += 26
    head_font = face(SERIF_BOLD, head_px)
    head_lines = wrap_text(ruler, headline, head_font, inner_w)
    cursor = draw_lines(ruler, inner_x, cursor, head_lines, head_font,
                        INK, head_px + 4)
    cursor += 4
    body_font = face(SANS, body_px)
    body_lines = wrap_text(ruler, body, body_font, inner_w)
    draw_lines(ruler, inner_x, cursor, body_lines, body_font,
               BODY_GREY, body_px + 6)
    return y + h


# 26 one-line brief items: (tag, text). Each must fit one line.
BRIEF_LEFT = [
    ("US", "Trump orders federal executions sped up, wider death penalty"),
    ("CONGRESS", "Gomez to quit Congress Dec 1 after ethics misconduct finding"),
    ("UN", "Guterres: agree a global AI risk framework within a year"),
    ("ISRAEL", "Eisenkot sees no imminent Iran threat; unity talks continue"),
    ("INDONESIA", "Candy factory fire: 24 dead, about 30 still missing"),
    ("GENEVA", "Geneva talks trim peace plan from 28 points to 19; no deal yet"),
    ("BEIRUT", "Israeli strike kills Hezbollah commander Tabtabai"),
    ("LONDON", "GTA VI hacker Kurtaj, 21, jailed 7 years, walks free same day"),
    ("KOREA", "US MQ-9 Reaper drone crashes off Gunsan; no injuries"),
    ("KHARKIV", "Russian drones hit Kharkiv: four dead, 13 wounded"),
    ("PAKISTAN", "Attack in Peshawar kills three security men, wounds five"),
    ("SYRIA", "Deadly attack on a couple in Homs sparks unrest and curfew"),
    ("RUSSIA", "FSB says it foiled railway sabotage in Altai; two shot dead"),
]

BRIEF_RIGHT = [
    ("CLIMATE", "COP31 fallout: Guterres frustrated; Gore blasts petrostates"),
    ("DELHI", "Nepal PM Shah meets Modi; India pledges Rs 15,000 crore aid"),
    ("JAKARTA", "Prabowo names VP picks: a loyalist and a tycoon's cousin"),
    ("LONDON", "Royal Navy shadows Russian warship, tanker off British coast"),
    ("SUDAN", "Saudis condemn drone strikes on Khartoum homes, UN building"),
    ("NATO", "Rutte: NATO will defend 'every inch', including in space"),
    ("CANADA", "Canada's PM brings Trump impersonator on stage at press gala"),
    ("NEW YORK", "Ms Rachel protests US child immigration hearings"),
    ("TRAVEL", "Storms, airline glitches threaten messy Thanksgiving travel"),
    ("PYONGYANG", "North Korea says it is ready to expand ties abroad"),
    ("BANGKOK", "Thai court upholds verdict against opposition lawmaker"),
    ("PARIS", "Macron eyes constitutional changes to curb spending"),
    ("BRITAIN", "Thousands evacuated from UK concert over 'unknown substance'"),
]


def build_sheet():
    """Compose the whole poster and return it as a PIL image."""
    sheet = Image.new("RGB", (SHEET_W, SHEET_H), PAPER)
    pen = ImageDraw.Draw(sheet)
    mid_x = SHEET_W // 2
    content_w = SHEET_W - 2 * EDGE
    cursor_y = 24

    # --- masthead ------------------------------------------------------
    mast_font = shrink_to_fit(SERIF_BOLD, "THE WORLD IN A DAY", 76,
                              content_w)
    pen.text((mid_x, cursor_y), "THE WORLD IN A DAY", font=mast_font,
             fill=INK, anchor="ma")
    pen.line([EDGE, 106, SHEET_W - EDGE, 106], fill=INK, width=3)
    pen.line([EDGE, 112, SHEET_W - EDGE, 112], fill=INK, width=1)
    spaced_line(pen, mid_x, 122,
                "TUESDAY \u00b7 24 NOVEMBER 2026 \u2014 38 STORIES",
                face(SANS_BOLD, 26), CRIMSON, 6)
    pen.line([EDGE, 158, SHEET_W - EDGE, 158], fill=INK, width=1)
    cursor_y = 168

    # --- hero story: the Merkury sunk off Libya ------------------------
    hero_text = (
        "Seven Ukrainian sea drones sink the corvette Merkury off Libya "
        "and hit the cargo ship MV Angara \u2014 2,400 km from the "
        "front. A Ka-27 helicopter aboard is destroyed; satellite "
        "images show the ship capsized in Benghazi harbour."
    )
    hero_inner_w = content_w - 32 - 190
    hero_head_lines = wrap_text(pen, "UKRAINE SINKS RUSSIAN WARSHIP",
                                face(SERIF_BOLD, 32), hero_inner_w)
    hero_body_lines = wrap_text(pen, hero_text, face(SANS, 18),
                                hero_inner_w)
    hero_h = (14 + 28 + len(hero_head_lines) * 36 + 6
              + len(hero_body_lines) * 23 + 12)
    pen.rectangle([EDGE, cursor_y, SHEET_W - EDGE - 1,
                   cursor_y + hero_h - 1], outline=INK, width=2)
    paint_sinking_ship(pen, SHEET_W - EDGE - 96, cursor_y + hero_h // 2)
    hx = EDGE + 16
    hy = cursor_y + 14
    pen.text((hx, hy), "BENGHAZI \u00b7 THE WAR AT SEA",
             font=face(SANS_BOLD, 20), fill=CRIMSON)
    hy += 28
    hero_font = face(SERIF_BOLD, 32)
    hy = draw_lines(pen, hx, hy, hero_head_lines, hero_font, INK, 36)
    hy += 6
    hero_body = face(SANS, 18)
    draw_lines(pen, hx, hy, hero_body_lines, hero_body, BODY_GREY, 23)
    cursor_y += hero_h + 5

    # --- second row: two stories ---------------------------------------
    half_w = (content_w - 8) // 2
    nv_head_n, nv_body_n = measure_story(
        pen, "HUANG IS BACK AT NVIDIA",
        "The board unanimously reinstates Jensen Huang, 11 days after "
        "he quit over affairs including one with an alleged Chinese "
        "spy; shares jump 33%.",
        24, 16, half_w - 28)
    sp_head_n, sp_body_n = measure_story(
        pen, "A NUCLEAR WEAPON IN ORBIT?",
        "Western intelligence warns Russia could launch Sputnik-S, a "
        "satellite built to carry a nuclear warhead, as soon as "
        "December. NATO vows to defend space.",
        24, 16, half_w - 28)
    row2_h = max(box_height(nv_head_n, nv_body_n, 24, 16),
                 box_height(sp_head_n, sp_body_n, 24, 16))
    story_box(pen, EDGE, cursor_y, half_w, row2_h,
              "SILICON VALLEY \u00b7 NVIDIA",
              "HUANG IS BACK AT NVIDIA",
              "The board unanimously reinstates Jensen Huang, 11 days after "
              "he quit over affairs including one with an alleged Chinese "
              "spy; shares jump 33%.",
              24, 16)
    story_box(pen, EDGE + half_w + 8, cursor_y, half_w, row2_h,
              "SPACE \u00b7 THE NEW ARMS RACE",
              "A NUCLEAR WEAPON IN ORBIT?",
              "Western intelligence warns Russia could launch Sputnik-S, a "
              "satellite built to carry a nuclear warhead, as soon as "
              "December. NATO vows to defend space.",
              24, 16)
    cursor_y += row2_h + 5

    # --- third row: three stories --------------------------------------
    third_w = (content_w - 16) // 3
    ee_head_n, ee_body_n = measure_story(
        pen, "MOSCOW WARNS ESTONIA OF WAR",
        "Russia accuses Estonia of acts \u2018on the verge of "
        "triggering open war\u2019 as Tallinn shuts the border.",
        24, 15, third_w - 28)
    toll_head_n, toll_body_n = measure_story(
        pen, "470,000 RUSSIAN WAR DEAD",
        "Hacked records put Russian war deaths at 470,000 at least; "
        "the true toll may top 700,000.",
        24, 15, third_w - 28)
    grok_head_n, grok_body_n = measure_story(
        pen, "TWO STATES SUE OVER GROK",
        "Virginia and Oregon sue Musk\u2019s SpaceX: Grok\u2019s "
        "\u2018spicy mode\u2019 made sexualised images.",
        24, 15, third_w - 28)
    row3_h = max(box_height(ee_head_n, ee_body_n, 24, 15),
                 box_height(toll_head_n, toll_body_n, 24, 15),
                 box_height(grok_head_n, grok_body_n, 24, 15))
    story_box(pen, EDGE, cursor_y, third_w, row3_h,
              "TALLINN \u00b7 NATO\u2019S EDGE",
              "MOSCOW WARNS ESTONIA OF WAR",
              "Russia accuses Estonia of acts \u2018on the verge of "
              "triggering open war\u2019 as Tallinn shuts the border.",
              24, 15)
    story_box(pen, EDGE + third_w + 8, cursor_y, third_w, row3_h,
              "THE HIDDEN TOLL",
              "470,000 RUSSIAN WAR DEAD",
              "Hacked records put Russian war deaths at 470,000 at least; "
              "the true toll may top 700,000.",
              24, 15)
    story_box(pen, EDGE + 2 * (third_w + 8), cursor_y, third_w, row3_h,
              "WASHINGTON \u00b7 AI & THE LAW",
              "TWO STATES SUE OVER GROK",
              "Virginia and Oregon sue Musk\u2019s SpaceX: Grok\u2019s "
              "\u2018spicy mode\u2019 made sexualised images.",
              24, 15)
    cursor_y += row3_h + 5

    # --- in brief: 26 more stories, two columns ------------------------
    pen.text((EDGE, cursor_y), "IN BRIEF \u2014 26 MORE STORIES",
             font=face(SANS_BOLD, 17), fill=CRIMSON)
    pen.text((SHEET_W - EDGE, cursor_y),
             "SOURCES: REUTERS \u00b7 AP \u00b7 CNN \u00b7 AL JAZEERA \u00b7 WSJ \u00b7 XINHUA \u00b7 AFP \u00b7 UN",
             font=face(SANS, 12), fill=BODY_GREY, anchor="ra")
    cursor_y += 24
    col_w = (content_w - 12) // 2
    brief_font = face(SANS, 13)
    tag_font = face(SANS_BOLD, 13)
    for col, items in ((EDGE, BRIEF_LEFT),
                       (EDGE + col_w + 12, BRIEF_RIGHT)):
        y = cursor_y
        for tag, text in items:
            tag_w = pen.textlength(tag + "  ", font=tag_font)
            text_w = col_w - tag_w
            item_font = brief_font
            size = 13
            while size > 10 and pen.textlength(text, font=item_font) > text_w:
                size -= 1
                item_font = face(SANS, size)
            pen.text((col, y), tag, font=tag_font, fill=CRIMSON)
            pen.text((col + tag_w, y), text, font=item_font, fill=INK)
            y += 18
    cursor_y += len(BRIEF_LEFT) * 18 + 5

    # --- ticker: two lines, six items ---------------------------------
    tick_h = 46
    pen.rectangle([EDGE, cursor_y, SHEET_W - EDGE - 1,
                   cursor_y + tick_h - 1], fill=INK)
    tick_lines = [
        "ALSO:  Kyiv strikes kill at least 14  \u00b7  "
        "Vance is Trump's envoy to Nvidia board  \u00b7  "
        "N. Korea may shut Swiss office",
        "Trump pauses explosives detonation  \u00b7  "
        "China media hits out at \u2018deflation trap\u2019 talk  \u00b7  "
        "Ibaraki briefs on nuclear-waste survey",
    ]
    for i, tick_text in enumerate(tick_lines):
        tick_font = shrink_to_fit(SANS_BOLD, tick_text, 15,
                                  content_w - 24)
        assert tick_font.size >= 11, "ticker line %d too wide" % i
        pen.text((mid_x, cursor_y + 8 + i * 20), tick_text,
                 font=tick_font, fill=PAPER, anchor="ma")
    cursor_y += tick_h
    print("layout ends at y=%d (sheet %d)" % (cursor_y, SHEET_H))
    assert cursor_y <= SHEET_H - 8, "layout overflow: ends %d" % cursor_y
    return sheet


def main():
    poster = build_sheet()
    here = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(here, "entry.png")
    poster.save(target, format="PNG")
    print("wrote %s (%dx%d)" % (target, poster.width, poster.height))


if __name__ == "__main__":
    main()
