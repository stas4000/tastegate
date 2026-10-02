---
name: tastegate
description: Build or fix a frontend (landing page, marketing site, dashboard, app screen, component) so it looks designed, not AI-generated, and prove it in a real browser before calling it done. Picks a design direction first (taste), builds on a craft floor (impeccable-style rules), then runs scripts/gate.py, which renders the page at phone and desktop width and fails on overlapping text, sideways scroll, low contrast, tiny tap targets, AI purple gradients, gradient text, emoji icons, eyebrow labels, default fonts, three-equal-card grids and placeholder copy. Use for any UI build, redesign, polish or "make it look better" request.
license: "MIT (derived parts: see THIRD_PARTY_NOTICES.md)"
---

# tastegate

Two skills in one, plus the part both leave to the model: proof.

1. **Taste** decides what the page should be before any code (from taste-skill, MIT).
2. **The craft floor** holds the mechanics every page must meet (from impeccable, Apache-2.0).
3. **The gate** renders the page in a real browser at phone and desktop width and refuses "done" while any hard finding is open. A model that wrote the CSS cannot see that its hero overlaps its nav at 390px. The browser can.

Work through the four steps in order. Do not announce the checklists; apply them.

## Step 1. Read the room (2 minutes, before code)

Write one line before building:

> Reading this as: <page kind> for <audience>, in a <vibe> language, built on <type pairing> + <palette family> + <one signature detail>.

- The audience picks the look, not your habit. A B2B buyer, a design-savvy consumer and a public-sector visitor need three different pages.
- Set three dials from the read (1 to 10): **variance** (symmetry to art), **motion** (still to cinematic), **density** (gallery to cockpit). Default landing page: 7 / 6 / 4. Trust-first or regulated: 3 / 2 / 5.
- Name one **signature detail** the page will be remembered by: a type treatment, a material, an interaction, a way the product is shown. One, done well.
- If the brief pins fonts, colors or an era, the brief wins over every rule here.

Full direction rules: [references/direction.md](references/direction.md).

## Step 2. Build on the craft floor

Read [references/craft-floor.md](references/craft-floor.md) right before the first UI edit. The short version:

- **Type:** a real display face with character, self-hosted or from a font service, paired with a readable text face. Not Inter, Roboto, Arial or the system stack as the display voice unless the brief asks for neutral. Body 16px or more, 60 to 75 characters a line, headings balanced, clear size and weight steps.
- **Color:** one neutral family, one accent, locked across the whole page. No purple-to-blue "AI glow" gradients, no gradient text, no colored glow halos. Secondary text tinted from its surface, never plain gray on color. Body contrast 4.5:1 or better.
- **Layout:** the hero fits the first screen with its call to action visible. No small uppercase eyebrow label over every heading. No row of three same-size cards (icon, heading, text) as the page's structure. Each section uses a different layout family. Spacing is tighter inside a group than between groups.
- **Icons and copy:** real SVG icons in one stroke weight, never emoji. The product's own words: no lorem ipsum, no "Acme", no "John Doe", no em dashes in body copy, no "Unlock the power of".
- **States:** hover, focus-visible, active, disabled, loading, empty and error exist for every control that has them. Style the browser parts too: selection color, focus ring, scrollbar, caret.
- **Motion:** one authored moment, eased out, from an already-visible default. Respect `prefers-reduced-motion`.
- **Phone first:** every multi-column block declares what it becomes under 768px. Tap targets at least 44px. Nothing scrolls sideways.

## Step 3. Run the gate

```bash
python3 <skill-dir>/scripts/gate.py <path/to/index.html or http://localhost:3000> --out .tastegate
```

It renders the page in headless Chromium at 390x844 and 1440x900, prints every finding with its rule, viewport and element, saves full-page screenshots, and exits 1 while any **fail** finding is open. First run only: `pip install playwright && python3 -m playwright install chromium`.

Fix every fail finding in one batch, then run the gate again. Warnings are judgment calls: fix them unless the brief asked for that thing.

## Step 4. Look at it yourself

Open both screenshots the gate saved (`.tastegate/desktop.png`, `.tastegate/mobile.png`). The gate catches mechanics; it cannot tell you the page is boring. Ask: would a designer at a good studio ship this? Does the signature detail land in the first viewport? Is anything still a default you did not choose? Fix what you see, rerun the gate, and stop after that round.

## Done means

- The gate exits 0 on the final files.
- You opened both screenshots after the last change.
- Every requirement in the brief is on the page and findable in seconds.

Report the gate's last line and the screenshot paths with your result. "Looks good" without them is not done.
