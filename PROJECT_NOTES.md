# Project Notes — Logic Pro Articulation Sets

Working notes / context dump for this repo. The README is the user-facing doc;
this file is the "everything we figured out" reference.

## Goal

Programmatically generate Logic Pro Articulation Sets (`.plist`) for Kontakt
libraries so keyswitches become named, notatable articulations you can select
from the track header, draw in the Piano Roll, or record by playing the
keyswitch keys.

- DAW: Logic Pro (macOS)
- Generator: `gen_artic.py` (edit `LIBRARIES`, rerun)
- Output: `sets/*.plist`
- Install: `install.sh` copies `sets/` → `~/Music/Audio Music Apps/Articulation Settings/`
  (restart Logic; assign from a track's Articulation Set menu)

## How Logic Articulation Sets work (the schema we reverse-engineered)

Learned by reading a factory set:
`/Applications/Logic Pro.app/Contents/Resources/Articulation Settings/Studio Horns/Studio Trumpet 1.plist`

A set is an XML plist with these top-level keys:

- `Articulations` (array) — each has:
  - `ArticulationID` (int, 1..N) — the ID referenced by notes in a region
  - `ID` (int, we use `1000 + ArticulationID`)
  - `Name` (string) — cosmetic label
  - `Symbol` (string, optional) — notation symbol (see valid list below)
  - `Default` (`<true/>`, optional) — default articulation (we set on slot 1)
  - `Output` (array) — MIDI Logic SENDS to Kontakt when this artic is active.
    Each entry: `MB1` (note number), `Status` = **`Note On`** (with a space)
- `Switches` (array) — input keyswitches Logic LISTENS for. Each entry:
  - `ID` (int) — references the articulation's `ID` (the 1000+ number)
  - `MB1` (note number)
  - `Mode` (string) — `Permanently` (latch until another) or
    `Momentary Trigger` (active only while held; for one-shots)
  - `Status` = **`NoteOn`** (NO space — differs from Output on purpose!)
- `InputMidiChannel` (int) — `-1` = omni
- `OctaveOffset` (int) — `0`
- `SwitchingEnabled` (`<true/>`/`<false/>`) — we set `true` so playing/clicking
  a keyswitch selects the articulation

### Gotchas
- **`Note On` (Output) vs `NoteOn` (Switches)** — the space matters.
- Validate every file with `plutil -lint`.
- Filenames contain the display name; the plist's `Name` key mirrors the filename.

### Valid notation `Symbol` strings (from factory sets)
`Staccato`, `Staccatissimo`, `Marcato`, `Marcatissimo`, `Pizzicato`,
`Fall Long`, `Fall Short`, `Doit Short`, `Scoop Long`, `Scoop Short`.

Our auto-mapping (`SYMBOLS` in the generator): staccato→Staccato,
spiccato/staccatissimo→Staccatissimo, marcato→Marcato,
sforzando/sforzato→Marcatissimo, pizz→Pizzicato, fall→Fall Short,
doit→Doit Short, scoop→Scoop Short.

One-shots that get `Momentary Trigger` (`MOMENTARY_HINTS`): fall, rip, doit,
scoop, shake, flutter.

## Conventions

- **Base keyswitch note:** slot 1 = C0 = MIDI **24** in Logic (where C3 = 60).
  Slots run chromatically upward (C0, C#0, D0, …).
- **Per-library base override:** `BASE_BY_PREFIX`. Session Horns Pro uses C-1 = 12.
- **Naming:** `NI - SE - <Library> - <Instrument>.plist` for NI Symphony
  Essentials; `Session Horns Pro - <Instrument>.plist` for e-instruments SHP.
  Instrument display names have the " Essential" suffix stripped and use the
  real (often plural) Kontakt names.
- **Slot order ↔ note number is what switches the sound. Names/symbols are cosmetic.**

## Why names had to be verified by screenshot

The `.nki` files are NKS-encrypted — the per-instrument slot names can't be read
programmatically (tried zlib/utf-16/latin-1 string extraction; nothing). So the
keyswitch *notes* are known (chromatic from the base), but *names* were verified
by reading each instrument's Kontakt **Articulation Slots** menu from screenshots.

Libraries live on an external drive:
`/Volumes/LaCie/native_instruments/shared/…` (content dirs come from
`/Users/Shared/Native Instruments/installed_products/*.json`).

## Status

### ✅ Verified (real Kontakt slot names)

**NI Symphony Essentials — Brass Solo** (base C0)

| Instrument | Slots (C0→) |
|---|---|
| Trumpet | Sustain p · Sustain f · Staccato Velocity · Staccato Triple Tongue · Sustain Str. Mute · Sforzando Mute · Swell Medium · Staccato Velocity |
| Horn 1 | Sustain p · Sustain f · Staccato Velocity · Staccato Triple Tongue · Staccato Tongue Stop · Sforzando Fast · Swell Fast · Blast FFF |
| Horn 2 | Sustain p · Sustain f · Staccato Velocity · Staccato Dbl. Tongue · Bend Stopped · Sforzando Fast · Swell Fast · Blast Short FFF |
| Trombone | Sustain p · Sustain f · Staccato Velocity · Staccato Triple Tongue · Staccato FFF · Sforzando Fast · Swell Fast · Tongue Stop |
| Tuba | Sustain p · Sustain f · Staccato Velocity · Staccato Dbl. Tongue · Crescendo · Sforzando Fast · Swell Fast · Staccato Tongue Stop |
| Brass Quartet | Sustain p · Sustain f · Staccato p · Staccato F · Sforzando Fast · Sforzando Slow *(6 slots, C0–F0)* |

**NI Symphony Essentials — Brass Ensemble** (base C0)

| Instrument | Slots (C0→) |
|---|---|
| Horns | Sustain All · Sustain Single Tongue · Trill Semi-Tone · Staccato · Staccato Stop Mute · Sforzando · Swell · Blast FFF |
| Trumpets | Sustain All · Sustain Double Tongue · Trill Semi-Tone · Staccato · Staccato Triple Tongue · Sforzando · Swell · Blast FFF |
| Trombones | Sustain All · Sustain Str. Mute · Sustain Trill Tongued · Staccato · Staccato Triple Tongue · Sforzando · Swell · Blast FFF |
| Tubas | Sustain All · Sustain Decrescendo · Sustain Trill · Staccato · Blast Short FFF · Sforzando · Swell Fast · Blast Long FFF |
| Brass Ensemble | Sustain · Staccato · Decrescendo · Sforzando · Crescendo · Swell · Blast FFF · Staccato Velocity |

**e-instruments — Session Horns Pro** (base C-1 / MIDI 12)

Shared default layout (8 slots, C-1→G-1):
`Non Vibrato · Vibrato · FoPiCre 2Beat · Grace · Grace Vibrato · Growl · Staccato · Rips`
— Trumpet 1, Trumpet 2, Tuba, Tenor Trombone, Tenor Sax, Mute Trumpet,
Flugelhorn, Bass Trombone, Alto Sax.

Exception — **Baritone Sax**: same 8 + a 9th keyswitch at G#-1 = `Non Vibrato`
(redundant duplicate of slot 1; 9 slots, C-1→G#-1).

**e-instruments — Session Strings Pro 2** (base C-1 / MIDI 12)

Verified from Kontakt (Key Switch panel, 3x3 grid, all nine slots filled):
`C-1 Sustain · C#-1 Staccato · D-1 Pizzicato · D#-1 Legato · E-1 Tremolo ·
F-1 Spiccato · F#-1 Forte Piano · G-1 Trill Semi · G#-1 Cresc Fast`

Labels match the panel exactly (`Forte Piano`, `Trill Semi`, `Cresc Fast`) rather
than NI's marketing names (`FortePiano`, `Trill semitone`, `Crescendo fast`).
Symbols: Staccato, Pizzicato, Staccatissimo (Spiccato), Marcatissimo (Forte
Piano). Tremolo / Trill / Cresc have no valid Logic symbol, so they render plain.

The library offers 26 articulations but only nine switchable slots per nki; the
rest (variant crescendi, trills, slides, scoops, falls, Portamento, Glissando)
are reachable only from the instrument's own menu. Documented in the generator
as a deliberate choice, not an oversight.

Note: the manual (p.19) shows `C-2` and only three slots — that screenshot is
stale; the shipping instrument starts at C-1.

### ⏳ Not yet verified (still on placeholder default names)

- **NI SE — String Ensemble** (base C0): Violins 1, Violins 2, Violas, Cellos,
  Basses, String Ensemble
  — placeholder: Sustain · Legato · Spiccato · Staccato · Pizzicato · Tremolo · Trill · Marcato
- **NI SE — Woodwind Ensemble** (base C0): Flutes, Oboes, Clarinets, Bassoons,
  Saxophones, Bass Winds, Woodwind Ensemble
  — placeholder: Sustain · Legato · Staccato · Marcato · Sforzando · Swell · Trill · Sustain fp
- **NI SE — Woodwind Solo** (base C0): Flute, Oboe, Clarinet, Bassoon,
  Contrabassoon, Saxophone, Woodwind Quintet
  — placeholder: Sustain · Sustain Vibrato · Legato · Staccato · Sforzando · Swell · Trill · Marcato

To verify: open each `.nki` in Kontakt, read the Articulation Slots menu
top-to-bottom, edit the matching list in `LIBRARIES`, rerun `gen_artic.py`.

## Open items

- **Old hand-made files:** `NI - SE - Brass Ensemble - Trombone.plist` and
  `… Trumpet.plist` (singular, output-only, no switches/symbols) predate this
  repo and live in the Logic folder. The generated versions are plural
  (`Trombones`, `Trumpets`), so both would appear in Logic. Decide whether
  `install.sh` should delete the old singular ones.
- **Baritone Sax label:** the screenshot labeled "Baritone Trombone" actually
  showed "Baritone Sax" in the UI — filed as `Baritone Sax`.
- **Baritone Sax 9th slot:** redundant 2nd "Non Vibrato" — keep or trim to 8.
- **Not yet installed:** nothing has been copied into Logic's library yet;
  run `install.sh` when ready.

## Git

Repo: `/Users/dmaida/repos/logic_articulation_sets` (branch `main`).
History: initial commit → brass verified + Brass Ensemble → Session Horns Pro
base-note support → remaining Session Horns Pro instruments.
