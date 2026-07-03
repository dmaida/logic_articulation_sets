# Logic Pro Articulation Sets — NI Symphony Essentials

Programmatically generated [Logic Pro Articulation Sets](https://support.apple.com/guide/logicpro/articulation-management-lgcpb1e9b8b5/mac)
for the **Native Instruments Symphony Essentials** orchestral libraries (in Kontakt).

Each set turns the library's keyswitches into named, notatable articulations you
can select from Logic's track header, draw in the Piano Roll, or record by playing
the keyswitch keys.

## What's generated

`gen_artic.py` writes 26 `.plist` files into `sets/`:

| Library | Instruments |
|---|---|
| Brass Solo | Trumpet, Horn 1, Horn 2, Trombone, Tuba, Brass Quartet |
| String Ensemble | Violins 1/2, Violas, Cellos, Basses, String Ensemble |
| Woodwind Ensemble | Flutes, Oboes, Clarinets, Bassoons, Saxophones, Bass Winds, Woodwind Ensemble |
| Woodwind Solo | Flute, Oboe, Clarinet, Bassoon, Contrabassoon, Saxophone, Woodwind Quintet |

## How the mapping works

Each Essentials instrument exposes up to **8 Articulation Slots** in Kontakt,
switched by 8 consecutive keys starting at **C0 (MIDI note 24)**:

```
slot 1 -> C0 (24)   slot 5 -> E0 (28)
slot 2 -> C#0 (25)  slot 6 -> F0 (29)
slot 3 -> D0 (26)   slot 7 -> F#0 (30)
slot 4 -> D#0 (27)  slot 8 -> G0 (31)
```

Every set has two halves that share those 8 keys:

- **`Output`** — when an articulation is active, Logic *sends* the keyswitch note
  to Kontakt to select the slot (`Status = Note On`).
- **`Switches`** — Logic *listens* for the keyswitch on input, so playing/clicking
  a key *selects* the articulation and records it into the region
  (`Status = NoteOn`). Normal articulations latch (`Permanently`); one-shot
  gestures (fall/rip/doit/scoop/shake/flutter) are `Momentary Trigger`.

Articulations also carry a notation **`Symbol`** where a valid Logic symbol exists
(Staccato, Staccatissimo/Spiccato, Marcato, Marcatissimo/Sforzando, Pizzicato…),
so they render in Score and Piano Roll.

**Slot order ↔ note number is what actually switches the sound. Names and symbols
are cosmetic.**

## Important: verify the slot names

The keyswitch *notes* are correct (8 keys from C0 = the Kontakt default). The
articulation *names* are educated defaults taken from each library's manual — the
`.nki` files are NKS-encrypted, so the real per-instrument slot list can't be read
programmatically.

To make the labels exact: open each `.nki` in Kontakt, click the articulation
label to show the **Articulation Slots** list, read the 8 names top-to-bottom, and
edit the matching list in `LIBRARIES` inside `gen_artic.py`. Then regenerate.

## Usage

```bash
python3 gen_artic.py     # regenerate sets/ after editing LIBRARIES
./install.sh             # copy sets/ -> ~/Music/Audio Music Apps/Articulation Settings/
```

Restart Logic Pro, then assign a set from a track's **Articulation Set** menu
(Track inspector). Playing C0–G0 (or clicking the articulation dots) switches
articulations.

### Knobs in `gen_artic.py`

- `BASE` — MIDI note of slot 1 (default `24` = C0). Change if your Kontakt
  keyswitch base differs.
- `SWITCHING_ENABLED` — `True` lets you select articulations by playing the
  keyswitch keys. Set `False` for output-only sets.
- `LIBRARIES` — the per-instrument slot lists (edit these to match Kontakt).
