#!/usr/bin/env python3
"""
Generate Fresh editor theme JSON files for all four Catppuccin flavors.

Reference theme schemas:
  https://github.com/sinelaw/fresh/blob/master/crates/fresh-editor/themes/nord.json
  https://github.com/sinelaw/fresh/blob/master/crates/fresh-editor/themes/dracula.json

Palette values verified against https://catppuccin.com/palette/
Role assignments follow the Catppuccin style guide conventions.
"""

import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Canonical Catppuccin palettes (verified against catppuccin.com/palette)
# Keys are the official color names; values are [R, G, B] 0-255.
# ---------------------------------------------------------------------------

PALETTES = {
    "latte": {
        "rosewater": [220, 138, 120], "flamingo":  [221, 120, 120],
        "pink":      [234, 118, 203], "mauve":     [136,  57, 239],
        "red":       [210,  15,  57], "maroon":    [230,  69,  83],
        "peach":     [254, 100,  11], "yellow":    [223, 142,  29],
        "green":     [ 64, 160,  43], "teal":      [ 23, 146, 153],
        "sky":       [  4, 165, 229], "sapphire":  [ 32, 159, 181],
        "blue":      [ 30, 102, 245], "lavender":  [114, 135, 253],
        "text":      [ 76,  79, 105], "subtext1":  [ 92,  95, 119],
        "subtext0":  [108, 111, 133], "overlay2":  [124, 127, 147],
        "overlay1":  [140, 143, 161], "overlay0":  [156, 160, 176],
        "surface2":  [172, 176, 190], "surface1":  [188, 192, 204],
        "surface0":  [204, 208, 218], "base":      [239, 241, 245],
        "mantle":    [230, 233, 239], "crust":     [220, 224, 232],
    },
    "frappe": {
        "rosewater": [242, 213, 207], "flamingo":  [238, 190, 190],
        "pink":      [244, 184, 228], "mauve":     [202, 158, 230],
        "red":       [231, 130, 132], "maroon":    [234, 153, 156],
        "peach":     [239, 159, 118], "yellow":    [229, 200, 144],
        "green":     [166, 209, 137], "teal":      [129, 200, 190],
        "sky":       [153, 209, 219], "sapphire":  [133, 193, 220],
        "blue":      [140, 170, 238], "lavender":  [186, 187, 241],
        "text":      [198, 208, 245], "subtext1":  [181, 191, 226],
        "subtext0":  [165, 173, 206], "overlay2":  [148, 156, 187],
        "overlay1":  [131, 139, 167], "overlay0":  [115, 121, 148],
        "surface2":  [ 98, 104, 128], "surface1":  [ 81,  87, 109],
        "surface0":  [ 65,  69,  89], "base":      [ 48,  52,  70],
        "mantle":    [ 41,  44,  60], "crust":     [ 35,  38,  52],
    },
    "macchiato": {
        "rosewater": [244, 219, 214], "flamingo":  [240, 198, 198],
        "pink":      [245, 189, 230], "mauve":     [198, 160, 246],
        "red":       [237, 135, 150], "maroon":    [238, 153, 160],
        "peach":     [245, 169, 127], "yellow":    [238, 212, 159],
        "green":     [166, 218, 149], "teal":      [139, 213, 202],
        "sky":       [145, 215, 227], "sapphire":  [125, 196, 228],
        "blue":      [138, 173, 244], "lavender":  [183, 189, 248],
        "text":      [202, 211, 245], "subtext1":  [184, 192, 224],
        "subtext0":  [165, 173, 203], "overlay2":  [147, 154, 183],
        "overlay1":  [128, 135, 162], "overlay0":  [110, 115, 141],
        "surface2":  [ 91,  96, 120], "surface1":  [ 73,  77, 100],
        "surface0":  [ 54,  58,  79], "base":      [ 36,  39,  58],
        "mantle":    [ 30,  32,  48], "crust":     [ 24,  25,  38],
    },
    "mocha": {
        "rosewater": [245, 224, 220], "flamingo":  [242, 205, 205],
        "pink":      [245, 194, 231], "mauve":     [203, 166, 247],
        "red":       [243, 139, 168], "maroon":    [235, 160, 172],
        "peach":     [250, 179, 135], "yellow":    [249, 226, 175],
        "green":     [166, 227, 161], "teal":      [148, 226, 213],
        "sky":       [137, 220, 235], "sapphire":  [116, 199, 236],
        "blue":      [137, 180, 250], "lavender":  [180, 190, 254],
        "text":      [205, 214, 244], "subtext1":  [186, 194, 222],
        "subtext0":  [166, 173, 200], "overlay2":  [147, 153, 178],
        "overlay1":  [127, 132, 156], "overlay0":  [108, 112, 134],
        "surface2":  [ 88,  91, 112], "surface1":  [ 69,  71,  90],
        "surface0":  [ 49,  50,  68], "base":      [ 30,  30,  46],
        "mantle":    [ 24,  24,  37], "crust":     [ 17,  17,  27],
    },
}

IS_LIGHT = {"latte": True, "frappe": False, "macchiato": False, "mocha": False}


def mix(a, b, t):
    """Linear interpolation between two RGB colors. t in [0, 1]."""
    return [round(a[i] + (b[i] - a[i]) * t) for i in range(3)]


def build_theme(flavor: str) -> dict:
    p = PALETTES[flavor]
    light = IS_LIGHT[flavor]

    # Diff backgrounds: blend Base toward Green/Red. Light themes need a
    # gentler blend so the surface stays readable.
    add_t   = 0.18 if light else 0.22
    rem_t   = 0.18 if light else 0.22
    add_hi  = 0.32 if light else 0.40
    rem_hi  = 0.32 if light else 0.40

    diff_add_bg            = mix(p["base"], p["green"], add_t)
    diff_remove_bg         = mix(p["base"], p["red"],   rem_t)
    diff_add_highlight_bg  = mix(p["base"], p["green"], add_hi)
    diff_remove_highlight_bg = mix(p["base"], p["red"], rem_hi)

    # Diagnostic backgrounds: very subtle tint of base toward the diag color.
    diag_t = 0.10 if light else 0.18
    error_bg   = mix(p["base"], p["red"],    diag_t)
    warning_bg = mix(p["base"], p["yellow"], diag_t)
    info_bg    = mix(p["base"], p["teal"],   diag_t)
    hint_bg    = p["base"]

    # Text-on-accent: dark themes put `crust` on bright accents; light themes
    # put `base` on dark accents.
    on_accent = p["base"] if light else p["crust"]

    return {
        "name": f"catppuccin-{flavor}",

        "editor": {
            "bg":                       p["base"],
            "fg":                       p["text"],
            "cursor":                   p["rosewater"],
            "selection_bg":             p["surface2"],
            "current_line_bg":          p["surface0"],
            "line_number_fg":           p["overlay1"],
            "line_number_bg":           p["base"],
            "whitespace_indicator_fg":  p["surface1"],
            "diff_add_bg":              diff_add_bg,
            "diff_remove_bg":           diff_remove_bg,
            "diff_add_highlight_bg":    diff_add_highlight_bg,
            "diff_remove_highlight_bg": diff_remove_highlight_bg,
        },

        "ui": {
            # Tabs
            "tab_active_fg":       p["text"],
            "tab_active_bg":       p["base"],
            "tab_inactive_fg":     p["subtext0"],
            "tab_inactive_bg":     p["mantle"],
            "tab_separator_bg":    p["crust"],
            "tab_hover_bg":        p["surface0"],

            # Status bar
            "status_bar_fg":       on_accent,
            "status_bar_bg":       p["blue"],
            "status_palette_fg":   on_accent,
            "status_palette_bg":   p["mauve"],

            # Prompt (e.g. command palette input)
            "prompt_fg":           on_accent,
            "prompt_bg":           p["green"],
            "prompt_selection_fg": p["text"],
            "prompt_selection_bg": p["surface2"],

            # Popups
            "popup_border_fg":     p["surface2"],
            "popup_bg":            p["mantle"],
            "popup_selection_bg":  p["surface2"],
            "popup_selection_fg":  p["text"],
            "popup_text_fg":       p["text"],

            # Menus
            "menu_bg":             p["mantle"],
            "menu_fg":             p["text"],
            "menu_active_bg":      p["surface1"],
            # Style guide uses Lavender for active line numbers; extending
            # that convention to other "active" UI indicators.
            "menu_active_fg":      p["lavender"],
            "menu_dropdown_bg":    p["mantle"],
            "menu_dropdown_fg":    p["text"],
            "menu_highlight_bg":   p["mauve"],
            "menu_highlight_fg":   on_accent,
            "menu_border_fg":      p["surface1"],
            "menu_separator_fg":   p["surface1"],
            "menu_hover_bg":       p["surface0"],
            "menu_hover_fg":       p["text"],
            "menu_disabled_fg":    p["overlay0"],
            "menu_disabled_bg":    p["mantle"],

            # Autocomplete suggestions
            "suggestion_bg":           p["mantle"],
            "suggestion_selected_bg":  p["surface2"],

            # Help / cheatsheet bar
            "help_bg":              p["base"],
            "help_fg":              p["text"],
            "help_key_fg":          p["sky"],
            "help_separator_fg":    p["overlay0"],
            "help_indicator_fg":    p["red"],
            "help_indicator_bg":    p["base"],

            # Splits / scrollbar
            "split_separator_fg":         p["surface0"],
            "scrollbar_track_fg":         p["surface0"],
            "scrollbar_thumb_fg":         p["surface2"],
            "scrollbar_track_hover_fg":   p["surface1"],
            "scrollbar_thumb_hover_fg":   p["overlay1"],

            # Settings UI
            "settings_selected_bg": p["surface1"],
            "settings_selected_fg": p["text"],
        },

        "search": {
            # Style guide: "Search Background: Teal"
            "match_bg": p["teal"],
            "match_fg": p["crust"] if not light else p["base"],
        },

        "diagnostic": {
            # Style guide: Errors→Red, Warnings→Yellow, Information→Teal.
            # Hint isn't specified; Sky pairs naturally as a lighter cool hue.
            "error_fg":   p["red"],
            "error_bg":   error_bg,
            "warning_fg": p["yellow"],
            "warning_bg": warning_bg,
            "info_fg":    p["teal"],
            "info_bg":    info_bg,
            "hint_fg":    p["sky"],
            "hint_bg":    hint_bg,
        },

        "syntax": {
            "keyword":               p["mauve"],
            "string":                p["green"],
            "comment":               p["overlay2"],
            "function":              p["blue"],
            "type":                  p["yellow"],
            "variable":              p["text"],
            "constant":              p["peach"],
            "operator":              p["sky"],
            "punctuation_bracket":   p["overlay2"],
            "punctuation_delimiter": p["overlay2"],
        },
    }


def format_theme(theme: dict) -> str:
    """Pretty-print with compact RGB arrays on single lines."""
    # json.dumps with indent=2 puts each array element on its own line,
    # which is ugly for RGB triples. Re-flatten them.
    raw = json.dumps(theme, indent=2)
    # Collapse 3-int arrays back onto one line
    import re
    return re.sub(
        r"\[\s*(\d+),\s*(\d+),\s*(\d+)\s*\]",
        r"[\1, \2, \3]",
        raw,
    ) + "\n"


def main():
    out_dir = Path("/mnt/user-data/outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    for flavor in PALETTES:
        theme = build_theme(flavor)
        path = out_dir / f"catppuccin-{flavor}.json"
        path.write_text(format_theme(theme))
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
