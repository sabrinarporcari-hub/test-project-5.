---
name: "Al Maryah Island · AI Lifestyle Library"
description: "One exceptional day on the island, hung as a night-gallery exhibition: full-bleed frames, each opening into its own specimen record."
colors:
  night-ink: "#070b10"
  night-ink-raised: "#0c1219"
  night-ink-high: "#131b25"
  oxford: "#002b49"
  document-grey: "#e6e6e4"
  document-grey-deep: "#d6d6d3"
  bone-text: "#ece9e3"
  mist-text: "#b3b6bb"
  slate-text: "#858b93"
  paper-ink: "#10161d"
  paper-ink-muted: "#49505a"
  paper-ink-quiet: "#575e67"
  hairline: "rgba(236, 233, 227, .14)"
  hairline-strong: "rgba(236, 233, 227, .32)"
  hairline-ink: "rgba(16, 22, 29, .16)"
  sky-echo: "#9acaeb"
  oxford-echo: "#86aed0"
  vermilion-echo: "#ef7a5f"
  gold-echo: "#e6bb72"
  bronze-echo: "#d2a89b"
  bronze-oxford-echo: "#c9aaa3"
  vermilion: "#d14124"
  vermilion-on-paper: "#a5321b"
  harbour-blue: "#4d7fa3"
typography:
  display:
    fontFamily: "Archivo, Arial Narrow, sans-serif"
    fontSize: "clamp(2.4rem, 1.5rem + 4vw, 5rem)"
    fontWeight: 560
    lineHeight: 0.94
    letterSpacing: "0.005em"
    fontVariation: "'wdth' 68"
  display-xl:
    fontFamily: "Archivo, Arial Narrow, sans-serif"
    fontSize: "clamp(3rem, 1.6rem + 6.4vw, 6rem)"
    fontWeight: 560
    lineHeight: 0.94
    letterSpacing: "0.005em"
    fontVariation: "'wdth' 68"
  numeral:
    fontFamily: "Archivo, Arial Narrow, sans-serif"
    fontSize: "clamp(3rem, 2rem + 4vw, 5.6rem)"
    fontWeight: 300
    lineHeight: 0.78
    letterSpacing: "-0.01em"
    fontFeature: "'tnum' 1"
    fontVariation: "'wdth' 62"
  headline:
    fontFamily: "Archivo, Arial Narrow, sans-serif"
    fontSize: "clamp(1.5rem, 1.1rem + 1.8vw, 2.6rem)"
    fontWeight: 500
    lineHeight: 1
    fontVariation: "'wdth' 66"
  title:
    fontFamily: "Archivo, Arial Narrow, sans-serif"
    fontSize: "1.05rem"
    fontWeight: 600
    lineHeight: 1.1
    letterSpacing: "0.05em"
    fontVariation: "'wdth' 72"
  lead:
    fontFamily: "Source Serif 4, Cambria, Georgia, serif"
    fontSize: "clamp(1.2rem, 1rem + .8vw, 1.65rem)"
    fontWeight: 340
    lineHeight: 1.32
  body:
    fontFamily: "Source Serif 4, Cambria, Georgia, serif"
    fontSize: "clamp(1.02rem, .96rem + .25vw, 1.15rem)"
    fontWeight: 400
    lineHeight: 1.55
  prompt:
    fontFamily: "Source Serif 4, Cambria, Georgia, serif"
    fontSize: "clamp(1.25rem, 1rem + .9vw, 1.75rem)"
    fontWeight: 360
    lineHeight: 1.45
  label:
    fontFamily: "Archivo, Arial Narrow, sans-serif"
    fontSize: "0.74rem"
    fontWeight: 560
    letterSpacing: "0.12em"
    fontVariation: "'wdth' 80"
rounded:
  none: "0"
  hairline: "2px"
  pill: "999px"
  dot: "50%"
spacing:
  gutter: "clamp(16px, 4vw, 64px)"
  container: "1360px"
  chapter: "clamp(96px, 14vw, 200px)"
  block: "clamp(72px, 9vw, 140px)"
  head: "clamp(48px, 6vw, 88px)"
  rule-row: "1rem"
components:
  reveal-toggle:
    textColor: "{colors.bone-text}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: ".55em .7em .55em 1em"
  reveal-toggle-pressed:
    backgroundColor: "{colors.bone-text}"
    textColor: "{colors.night-ink}"
    rounded: "{rounded.pill}"
  button-outline:
    textColor: "{colors.bone-text}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: ".8em 1.2em"
  button-outline-hover:
    backgroundColor: "{colors.bone-text}"
    textColor: "{colors.night-ink}"
  chip:
    textColor: "{colors.mist-text}"
    rounded: "{rounded.pill}"
    padding: ".32em .7em"
  chip-pressed:
    backgroundColor: "{colors.bone-text}"
    textColor: "{colors.night-ink}"
    rounded: "{rounded.pill}"
  tick-tip:
    backgroundColor: "{colors.bone-text}"
    textColor: "{colors.night-ink}"
    typography: "{typography.label}"
    rounded: "{rounded.hairline}"
    padding: ".35em .6em"
  gate-tag:
    backgroundColor: "{colors.document-grey}"
    textColor: "{colors.night-ink}"
    typography: "{typography.label}"
    rounded: "{rounded.hairline}"
    padding: ".3em .55em"
  document-chapter:
    backgroundColor: "{colors.document-grey}"
    textColor: "{colors.paper-ink}"
  code-tree:
    backgroundColor: "{colors.night-ink-raised}"
    textColor: "{colors.bone-text}"
    rounded: "{rounded.none}"
    padding: "1.2rem 1.4rem"
---

# Design System: Al Maryah Island · AI Lifestyle Library

## Overview

**Creative North Star: "The Night Gallery Day"**

The library is hung as an exhibition after dark. A near-black, Oxford-tinted ground (night ink) holds photographs edge to edge, and the site is navigated as a single day on the island, 07:00 to 22:00. Every frame is both a picture on a wall and a specimen with a catalogue entry: hover or tap and the image steps back while its record wipes in from the edge, tinted by that frame's own colour echo.

The interface is made of type and hairlines, nothing else. Condensed Archivo capitals carry everything that is data (hours, labels, counts, parameter names, chapter statements); Source Serif 4 carries everything that is said (leads, prompts, reading copy), most often in italic. Structure comes from 1px rules at low opacity, never from cards, panels or fills. Density is gallery-sparse in the exhibit and catalogue-dense in the records and process chapters, where definition lists, numbered steps and tables sit on ruled rows.

Colour is mostly withheld. The ground is night ink, text is warm bone, and a single accent at a time comes from the photograph on show: the active frame (or the active chapter) sets `--echo`, and only that echo colours the current tick, the record's edge, the world line and the focus ring. One chapter (Prompt Architecture) flips to a neutral light document grey with ink text, following the source deck's own alternation of dark and light layouts.

**Key Characteristics:**
- Night-ink ground (#070b10), photographs full-bleed or at full column width, square-cornered.
- Two-family type system: condensed Archivo caps for data, Source Serif 4 (often italic) for voice.
- Hairline rules (1px, 14% bone) as the only structural device; no cards, no panels.
- One live accent at a time, the frame's colour echo, set per frame or per chapter.
- Slow exponential easing and clip-path wipes; content arrives, it never bounces.

## Colors

A withheld, near-monochrome night palette in which the photograph lends the only accent, one echo at a time.

### Primary
- **Echo (runtime accent)**: not a fixed colour but a slot (`--echo`) the build fills per frame or chapter. It defaults to Sky Echo and is reassigned from the frame's documented colour echo. It colours the current day-line tick, the record's left rule, the world label in the caption, active rail and anatomy items, highlighted prompt spans (18% mix), the record-state wash (9% mix into night ink), and the focus outline.
- **Sky Echo** (sky-echo): the default echo and the house blue. Also used directly for text selection, the final step of the idea chain, method terms, the Omni route, file-size tags, hero bars in the delivery plan, and the gate dots in Selection.
- **Gold Echo** (gold-echo): the fixed echo for the System and Scale chapters, where no single frame is on show.

### Secondary
- **Frame echoes**: Oxford Echo (oxford-echo), Vermilion Echo (vermilion-echo), Bronze Echo (bronze-echo) and Bronze-Oxford Echo (bronze-oxford-echo). Each is the light, legible-on-night ink of a frame's documented colour echo, assigned in the gallery data. Vermilion Echo doubles as the risk and warning ink (risk terms, compare-slider notes).
- **Oxford** (oxford): the island's brand blue in its true, dark form. Used only on the document chapter: it is the echo, selection colour and active-part highlight in the Prompt Architecture chapter.

### Tertiary
- **Vermilion** (vermilion): the gate diamond in the delivery plan and its legend. A signal, not a surface.
- **Vermilion on Paper** (vermilion-on-paper): the "excluded" label on the document chapter, where the light vermilion would fail.
- **Harbour Blue** (harbour-blue): the full-library bar in the delivery plan, the second series beside Sky Echo.

### Neutral
- **Night Ink** (night-ink): page ground, exhibit ground, and the text colour on any light fill (pressed chip, tooltip, gate tag).
- **Night Ink Raised / High** (night-ink-raised, night-ink-high): the folder-tree code block, the only tonal step up from the ground.
- **Bone Text** (bone-text): primary text, the slider handle and thumb, pressed and hover fills.
- **Mist Text** (mist-text): secondary copy, leads, definitions.
- **Slate Text** (slate-text): tertiary copy, labels, counters, captions, "Not yet recorded" gaps.
- **Hairline / Hairline Strong** (hairline, hairline-strong): every rule, chip border and track. Strong is for top rules that open a list of peers (gates, pipeline, ownership, close pair) and for the range track.
- **Document Grey / Document Grey Deep** (document-grey, document-grey-deep): the neutral light ground of the document chapter, the skip link and the pipeline gate tag. Neutral, not warm: it is the deck's light layout, not parchment.
- **Paper Ink / Muted / Quiet** (paper-ink, paper-ink-muted, paper-ink-quiet) with **Hairline Ink** (hairline-ink): text and rules on the document chapter, swapped in by re-binding the same custom properties.

### Named Rules
**The One Echo Rule.** Only one accent is live on a screen, and it comes from the photograph: the frame's echo in the exhibit, gold in System and Scale, Oxford on the document chapter. Sky Echo is the default, not a second accent.

**The Rebind Rule.** A chapter changes world by re-binding tokens (`--line`, `--text-2`, `--text-3`, `--echo`) on its container, never by writing new component colours. The paper chapter is the reference.

## Typography

**Display Font:** Archivo variable (with Arial Narrow, sans-serif), self-hosted, width axis 62% to 125%
**Body Font:** Source Serif 4 variable, roman and italic (with Cambria, Georgia, serif), self-hosted, optical sizing on
**Label/Mono Font:** Archivo at 80% width doubles as the label face and the code face (tabular figures)

**Character:** A condensed grotesque cut narrow for capitals and numerals reads like gallery wall labels and timetables; a warm, literary serif in italic supplies the curator's voice. Width, not weight, is the main lever on Archivo.

### Hierarchy
- **Display** (560, `wdth` 68, caps, 0.94 line-height, 0.005em): chapter statements in four sizes: xl for the threshold and close, l for chapter heads, m for sub-sections, s (`wdth` 75, 0.02em, 1.05) for small statements. Balanced wrapping; threshold and close statements capped at 11 to 12ch.
- **Numeral** (300, `wdth` 62, tabular, 0.78 to 0.9 line-height): the hour in the caption, world hours, tallies, pipeline numbers, the configurator count, proof stats. Light, very condensed and large: the day is told in numerals.
- **Headline** (500, `wdth` 66, caps, line-height 1): the idea chain values, the anatomy layer value, the record title (560, `wdth` 66, 0.95).
- **Title** (600, `wdth` 70 to 72, caps, 0.04 to 0.06em, about 1.05 to 1.25rem): step names, case titles, gate names, ownership terms, anatomy layer buttons.
- **Lead** (Source Serif 4 italic, 340, 1.32, max 38ch, mist text): the line under every chapter head and the close.
- **Body** (Source Serif 4, 400, 1.55): reading copy; notes cap at 62ch, rules at 64 to 70ch.
- **Prompt** (Source Serif 4, 360, 1.45, roman on the document chapter, italic in the record): generation prompts, the one place the serif is set large.
- **Label** (Archivo 560, `wdth` 80, caps, 0.12em, 0.7 to 0.74rem): definition terms, figure-caption heads, table heads, legends, credits, the counter and day-line ends.

### Named Rules
**The Data Wears Caps Rule.** Anything that is a value, a time, a count or a field name is set in condensed Archivo with tabular figures; anything that is a sentence is set in Source Serif 4. A field name never appears in serif and a statement never in labels.

**The Narrow Not Heavy Rule.** Emphasis in Archivo comes from width (62% to 80%) and size; weight stays between 300 and 600.

## Layout

A single long page in two modes. The exhibit fills the first viewport (100svh, minimum 560px): one frame full-bleed, wordmark and "Behind the image" toggle top, previous and next arrows at the edges, and a three-column bottom bar (caption with large hour beside the serif-italic moment title and the echo world line under it, day line from 07:00 to 22:00 with one tick per frame, counter `01 / 10`). Top and bottom gradient scrims keep the bar legible on bright frames and fade away in the record state.

Below it, story chapters sit in a centred column `min(100% - 2 × gutter, 1360px)` with a fluid gutter (16px to 64px). Chapters open with generous top padding (96px to 200px) and a head of display statement plus lead; blocks inside a chapter are separated by 72px to 140px. Two-up splits (roughly 1fr / 1.05fr to 1.2fr) appear from 900px; most lists use `auto-fit` grids with 200px to 260px minimum columns, so they reflow without breakpoints. Horizontal strips (contact sheets, pipeline, case studies) bleed past the column, snap per item and pad with the gutter.

A fixed chapter rail appears at the left edge once the exhibit is passed, shows only short dashes until hovered, and is removed below 1180px. At 760px and below, the bottom bar becomes two rows (caption and counter, then the full-width day line), the record becomes a bottom sheet (64svh), the world accordion stacks vertically, and multi-column definition grids collapse to one column.

## Elevation & Depth

The system is flat. There is no box-shadow elevation anywhere; depth comes from the photograph itself, from darkening (the leaving plate drops to 45% brightness, closed worlds sit at 72% brightness and 85% saturation), and from tonal washes (the record state tints the whole exhibit 9% toward the echo). Overlays on photographs use flat translucent night ink (`rgba(7,11,16,.35)` to `.7`) and linear-gradient scrims, not cards.

The only shadows in the build are soft, unoffset legibility halos on type and strokes that sit directly on photographs (the wordmark, the large caption hour, the arrow chevrons), plus a zero-blur 0.12em spread used as padding on highlighted prompt spans. None of them lifts a surface.

### Shadow Vocabulary
- **Photo halo** (`text-shadow: 0 1px 14px rgba(0,0,0,.45)` on the wordmark; `0 2px 30px rgba(0,0,0,.35)` on the hour; `filter: drop-shadow(0 1px 8px rgba(0,0,0,.5))` on arrows): only for marks laid over a photograph, to keep them legible on bright frames.
- **Highlight pad** (`box-shadow: 0 0 0 .12em <echo at 18%>`): extends a highlighted prompt span's tint past its glyphs; it is a fill, not a shadow.

### Named Rules
**The Lights Down Rule.** To bring one thing forward, dim everything else; never lift the thing with a shadow. The record wipes in while the frame darkens behind it.

## Shapes

Square by default. Photographs, figures, strips, tables and the code block have no radius. Rounding is reserved for three cases: a 2px softening on small light tags (day-line tooltip, gate tag, focus ring, the bar figure); full pills (999px) for the few pressable controls (reveal toggle, chips, the back-to-day link); and true circles for dots and handles (gate and pipeline markers at 7px, layer markers at 6px, the compare handle at 44px, range thumbs at 18px). Lines are 1px everywhere; the active tick thickens to 2px. Arrows are drawn as single non-scaling 1.1px strokes in inline SVG.

## Components

### Buttons
Quiet, outlined and pill-shaped; they invert to bone on night when engaged.
- **Shape:** full pill (999px).
- **Reveal toggle:** label type (0.72rem, `wdth` 78, 0.14em) on a 28% night-ink fill with a 28% bone border; a small circled `kbd` shows the keyboard shortcut. Hover lifts the border to 60%; pressed fills with bone text colour and night-ink text.
- **Outline link button (Back to the day):** label type (0.74rem, 0.14em), hairline-strong border, `.8em 1.2em` padding; hover fills bone with night-ink text.
- **Text button (Close record):** label type in mist text with a 0.3em-offset underline; hover to bone.
- **Nav arrows:** bare 1.1px chevrons at 62% opacity, 44px to 64px wide by 120px tall hit areas; hover or focus to full opacity with a 4px nudge outward.

### Chips
- **Style:** hairline border, transparent fill, mist text in Source Serif 4 at 0.86rem, pill radius, `.32em .7em` padding.
- **State:** hover raises the border to hairline-strong and text to bone; pressed (`aria-pressed`) fills bone with night-ink text. A dashed "more" chip marks non-interactive overflow.

### Cards / Containers
There are no cards. Grouping is a ruled row: a 1px hairline top border, 0.6rem to 1rem top padding, label-type term and serif definition below. The same pattern serves parameters, method, risks, deliverables, files, proof stats and ownership. Strong hairlines open rows of peers that carry a marker dot.

### Inputs / Fields
- **Range:** a 1px hairline-strong track with an 18px bone circular thumb, no fill. Used for the hour-of-day blend.
- **Compare slider:** an invisible full-surface range over two stacked images; a 1px bone line with a 44px outlined circular handle carrying two short ticks. Focus draws a 1.5px sky outline around the handle.
- **Focus (global):** 1.5px solid echo outline, 4px offset, 2px radius.

### Navigation
- **Day line:** a 1px track at 32% bone with 07:00 and 22:00 ends in label type. Each frame is a 1px, 9px tall tick; hover grows it to 16px in bone, current grows to 26px by 2px in the echo. Hovering a tick shows a bone tooltip with night-ink label text.
- **Counter:** condensed tabular numerals, current in bone, total at 66%.
- **Chapter rail:** label-type links behind 10px dashes; the current dash extends to 26px in the echo; names reveal on hover over a fading night-ink gradient (a document-grey gradient on the document chapter).

### Specimen Record (signature)
The frame's catalogue entry. On desktop it sits at the right edge (up to 620px or 42vw) and opens with a clip-path wipe from the right (1000ms, exponential ease) while the frame recedes and the exhibit takes a 9% echo wash. Content: a condensed caps title, the world and pillar line in echo-coloured label type directly beneath it, a meta line, the final prompt in serif italic between curly quotes, then a two-column ruled grid of all documented fields. Rows arrive in a staggered cascade (34ms apart). Undocumented fields are shown, not hidden: "Not yet recorded" in slate label type behind a 14px dash. On phones it becomes a bottom sheet with an echo-tinted ground and echo top rule.

### Day Worlds (signature)
A horizontal accordion of photographs. Closed worlds are dimmed with a vertical caps name and an echo hour; the open world grows to 4.2× and reveals its pillar and numbered moments. Transitions are flex-grow at 900ms. On phones it stacks as 76px rows that open to 460px.

## Do's and Don'ts

### Do:
- **Do** set every surface on night ink (#070b10) and let photographs run edge to edge or full column width with square corners.
- **Do** take the accent from the frame on show by setting `--echo` on the container; use gold for System and Scale and Oxford on the document chapter.
- **Do** set times, counts, field names and labels in condensed Archivo caps with tabular figures, and sentences in Source Serif 4.
- **Do** group content with 1px hairline top rules and generous vertical rhythm instead of containers.
- **Do** show missing data as "Not yet recorded" in slate label type; never omit the field.
- **Do** move with the exponential ease (`cubic-bezier(.16, 1, .3, 1)`) at slow durations (about 1100ms for scene changes) and reveal with clip-path wipes; honour reduced motion by cutting all of it.

### Don't:
- **Don't** use cards, panels or filled containers to group content; the ruled row is the container.
- **Don't** use box-shadow for elevation or frosted-glass panels; dim the surroundings instead.
- **Don't** run two accents at once or introduce a colour that is not a frame echo or a defined signal.
- **Don't** round photographs or figures; radius belongs only to pills, dots and 2px tags.
- **Don't** set Archivo bold and wide for emphasis; narrow it and scale it.
