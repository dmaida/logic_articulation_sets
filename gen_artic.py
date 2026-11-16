#!/usr/bin/env python3
"""
Generate Logic Pro Articulation Set (.plist) files for the
NI Symphony *Essentials* orchestral libraries (Brass Solo, String Ensemble,
Woodwind Ensemble, Woodwind Solo).

How the mapping works
---------------------
Each Essentials instrument exposes up to 8 "Articulation Slots" in Kontakt,
switched by 8 consecutive keys starting at C0 (MIDI note 24):
    slot 1 -> C0 (24) ... slot 8 -> G0 (31)

Each generated set has TWO halves that use the same 8 keys:
  * Articulations[].Output  -> what Logic SENDS to Kontakt to pick the slot
                               (Note On, note = 24 + slot index).
  * Switches[]              -> what Logic LISTENS for on input, so playing a
                               keyswitch (or clicking it) SELECTS that
                               articulation and records it into the region
                               (Status = "NoteOn", note = same key).
Plus each articulation can carry a notation Symbol so it shows in Score /
Piano Roll. Names are cosmetic; slot order <-> note number is what matters.

Usage
-----
  1. In Kontakt, open each .nki, click the articulation label to show the
     ARTICULATION SLOTS list, read the 8 slot names top-to-bottom.
  2. Edit the per-instrument lists below to match (order = slot order).
  3. python3 gen_artic.py          # writes .plist files into ./sets/
  4. ./install.sh                   # copies ./sets/ -> Logic (then restart Logic)
"""

import os

BASE = 24                        # MIDI note of slot 1  (C0 in Logic; C3 = 60)
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sets")
SWITCHING_ENABLED = True         # play/click a keyswitch to SELECT an articulation

# Per-library override for the slot-1 keyswitch note (defaults to BASE = C0).
# e-instruments Session Horns Pro puts its keyswitches at C-1 (MIDI 12).
# e-instruments Session Strings Pro 2 also starts at C-1 (MIDI 12), verified
# from the Key Switch panel of Violins - Modern (the manual's screenshot is
# stale: it shows C-2 and omits the Legato slot).
BASE_BY_PREFIX = {
    "Session Horns Pro - ": 12,          # C-1
    "Session Strings Pro 2 - ": 12,      # C-1
}

# --- notation symbols: only these strings are valid in Logic (from factory sets)
SYMBOLS = {
    "staccato": "Staccato",
    "staccatissimo": "Staccatissimo",
    "spiccato": "Staccatissimo",
    "marcato": "Marcato",
    "sforzando": "Marcatissimo",
    "sforzato": "Marcatissimo",
    "pizzicato": "Pizzicato",
    "pizz": "Pizzicato",
    "fall": "Fall Short",
    "doit": "Doit Short",
    "scoop": "Scoop Short",
}
# one-shot gestures that should only be active while the key is held
MOMENTARY_HINTS = ("fall", "rip", "doit", "scoop", "shake", "flutter")


def symbol_for(name):
    n = name.lower()
    for key, sym in SYMBOLS.items():
        if key in n:
            return sym
    return None


def mode_for(name):
    n = name.lower()
    return "Momentary Trigger" if any(h in n for h in MOMENTARY_HINTS) else "Permanently"


# Instrument display names have their " Essential" suffix stripped automatically.
# prefix -> { instrument display name : [slot1, slot2, ... up to 8] }
LIBRARIES = {
    "NI - SE - Brass Solo - ": {
        # all verified from Kontakt (keyswitches from C0; Quartet uses only 6):
        "Brass Quartet": ["Sustain p", "Sustain f", "Staccato p",
                          "Staccato F", "Sforzando Fast", "Sforzando Slow"],
        "Horn 1": ["Sustain p", "Sustain f", "Staccato Velocity",
                   "Staccato Triple Tongue", "Staccato Tongue Stop",
                   "Sforzando Fast", "Swell Fast", "Blast FFF"],
        "Horn 2": ["Sustain p", "Sustain f", "Staccato Velocity",
                   "Staccato Dbl. Tongue", "Bend Stopped", "Sforzando Fast",
                   "Swell Fast", "Blast Short FFF"],
        # verified from Kontakt (keyswitches C0-G0):
        "Trumpet": ["Sustain p", "Sustain f", "Staccato Velocity",
                    "Staccato Triple Tongue", "Sustain Str. Mute",
                    "Sforzando Mute", "Swell Medium", "Staccato Velocity"],
        "Trombone": ["Sustain p", "Sustain f", "Staccato Velocity",
                     "Staccato Triple Tongue", "Staccato FFF",
                     "Sforzando Fast", "Swell Fast", "Tongue Stop"],
        "Tuba": ["Sustain p", "Sustain f", "Staccato Velocity",
                 "Staccato Dbl. Tongue", "Crescendo", "Sforzando Fast",
                 "Swell Fast", "Staccato Tongue Stop"],
    },
    "NI - SE - Brass Ensemble - ": {
        # all verified from Kontakt (keyswitches C0-G0):
        "Brass Ensemble": ["Sustain", "Staccato", "Decrescendo", "Sforzando",
                           "Crescendo", "Swell", "Blast FFF",
                           "Staccato Velocity"],
        "Horns": ["Sustain All", "Sustain Single Tongue", "Trill Semi-Tone",
                  "Staccato", "Staccato Stop Mute", "Sforzando", "Swell",
                  "Blast FFF"],
        "Trumpets": ["Sustain All", "Sustain Double Tongue", "Trill Semi-Tone",
                     "Staccato", "Staccato Triple Tongue", "Sforzando",
                     "Swell", "Blast FFF"],
        "Tubas": ["Sustain All", "Sustain Decrescendo", "Sustain Trill",
                  "Staccato", "Blast Short FFF", "Sforzando", "Swell Fast",
                  "Blast Long FFF"],
        "Trombones": ["Sustain All", "Sustain Str. Mute",
                      "Sustain Trill Tongued", "Staccato",
                      "Staccato Triple Tongue", "Sforzando", "Swell",
                      "Blast FFF"],
    },
    "NI - SE - String Ensemble - ": {
        inst: ["Sustain", "Legato", "Spiccato", "Staccato",
               "Pizzicato", "Tremolo", "Trill", "Marcato"]
        for inst in ["Violins 1", "Violins 2", "Violas", "Cellos", "Basses",
                     "String Ensemble"]
    },
    "NI - SE - Woodwind Ensemble - ": {
        inst: ["Sustain", "Legato", "Staccato", "Marcato",
               "Sforzando", "Swell", "Trill", "Sustain fp"]
        for inst in ["Flutes", "Oboes", "Clarinets", "Bassoons",
                     "Saxophones", "Bass Winds", "Woodwind Ensemble"]
    },
    "NI - SE - Woodwind Solo - ": {
        inst: ["Sustain", "Sustain Vibrato", "Legato", "Staccato",
               "Sforzando", "Swell", "Trill", "Marcato"]
        for inst in ["Flute", "Oboe", "Clarinet", "Bassoon", "Contrabassoon",
                     "Saxophone", "Woodwind Quintet"]
    },
    # e-instruments Session Horns Pro (keyswitches at C-1, see BASE_BY_PREFIX).
    "Session Horns Pro - ": {
        # shared default layout, verified from Kontakt (keyswitches C-1 to G-1).
        **{inst: ["Non Vibrato", "Vibrato", "FoPiCre 2Beat", "Grace",
                  "Grace Vibrato", "Growl", "Staccato", "Rips"]
           for inst in ["Trumpet 1", "Trumpet 2", "Tuba", "Tenor Trombone",
                        "Tenor Sax", "Mute Trumpet", "Flugelhorn",
                        "Bass Trombone", "Alto Sax"]},
        # Baritone Sax adds a 9th keyswitch at G#-1 (a 2nd Non Vibrato):
        "Baritone Sax": ["Non Vibrato", "Vibrato", "FoPiCre 2Beat", "Grace",
                         "Grace Vibrato", "Growl", "Staccato", "Rips",
                         "Non Vibrato"],
    },
    # e-instruments Session Strings Pro 2 (keyswitches at C-1, see BASE_BY_PREFIX).
    # Nine keyswitch slots in a 3x3 grid, keys user-assignable per nki.
    # Verified from Kontakt (Violins - Modern, Key Switch panel):
    #   C-1 Sustain | C#-1 Staccato | D-1 Pizzicato | D#-1 Legato
    # Slots 5-9 (E-1 ... G#-1) are empty in that nki. Layout for the other
    # instruments (Violas/Celli/Basses/Ensemble) is assumed to match - verify.
    "Session Strings Pro 2 - ": {
        inst: ["Sustain", "Staccato", "Pizzicato", "Legato"]
        for inst in ["Violins", "Violas", "Celli", "Basses", "Ensemble"]
    },
}


def build_plist(fname, artics, base=BASE):
    art_rows, sw_rows = [], []
    for i, name in enumerate(artics):
        aid = i + 1
        iid = 1000 + aid
        note = base + i
        sym = symbol_for(name)
        sym_xml = (f"\n\t\t\t\t<key>Symbol</key>\n\t\t\t\t<string>{sym}</string>"
                   if sym else "")
        default_xml = "\n\t\t\t\t<key>Default</key>\n\t\t\t\t<true/>" if i == 0 else ""
        art_rows.append(f"""\t\t\t<dict>
\t\t\t\t<key>ArticulationID</key>
\t\t\t\t<integer>{aid}</integer>
\t\t\t\t<key>ID</key>
\t\t\t\t<integer>{iid}</integer>
\t\t\t\t<key>Name</key>
\t\t\t\t<string>{name}</string>{sym_xml}{default_xml}
\t\t\t\t<key>Output</key>
\t\t\t\t<array>
\t\t\t\t\t<dict>
\t\t\t\t\t\t<key>MB1</key>
\t\t\t\t\t\t<integer>{note}</integer>
\t\t\t\t\t\t<key>Status</key>
\t\t\t\t\t\t<string>Note On</string>
\t\t\t\t\t</dict>
\t\t\t\t</array>
\t\t\t</dict>""")
        sw_rows.append(f"""\t\t\t<dict>
\t\t\t\t<key>ID</key>
\t\t\t\t<integer>{iid}</integer>
\t\t\t\t<key>MB1</key>
\t\t\t\t<integer>{note}</integer>
\t\t\t\t<key>Mode</key>
\t\t\t\t<string>{mode_for(name)}</string>
\t\t\t\t<key>Status</key>
\t\t\t\t<string>NoteOn</string>
\t\t\t</dict>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
\t<key>Articulations</key>
\t<array>
{chr(10).join(art_rows)}
\t</array>
\t<key>InputMidiChannel</key>
\t<integer>-1</integer>
\t<key>Name</key>
\t<string>{fname}</string>
\t<key>OctaveOffset</key>
\t<integer>0</integer>
\t<key>Switches</key>
\t<array>
{chr(10).join(sw_rows)}
\t</array>
\t<key>SwitchingEnabled</key>
\t<{'true' if SWITCHING_ENABLED else 'false'}/>
</dict>
</plist>
"""


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    n = 0
    for prefix, insts in LIBRARIES.items():
        base = BASE_BY_PREFIX.get(prefix, BASE)
        for inst, artics in insts.items():
            fname = f"{prefix}{inst}.plist"
            with open(os.path.join(OUT_DIR, fname), "w", encoding="utf-8") as fh:
                fh.write(build_plist(fname, artics, base))
            n += 1
            print(f"wrote {fname}  ({len(artics)} artics, notes "
                  f"{base}-{base + len(artics) - 1})")
    print(f"\n{n} files -> {OUT_DIR}")


if __name__ == "__main__":
    main()
