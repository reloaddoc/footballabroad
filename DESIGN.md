---
name: Kickways
description: Career intelligence for realistic football career moves.
colors:
  accent-blue: "#2563eb"
  app-bg: "#0b0d12"
  sidebar-bg: "#0f1117"
  surface: "#11141b"
  surface-soft: "#151923"
  text: "#f8fafc"
  text-soft: "#cbd5e1"
  text-muted: "#94a3b8"
  border-muted: "rgba(148, 163, 184, 0.20)"
  border-accent: "rgba(37, 99, 235, 0.48)"
typography:
  display:
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "clamp(2.1rem, 4vw, 4rem)"
    fontWeight: 760
    lineHeight: 1.02
    letterSpacing: "0"
  headline:
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "1.35rem"
    fontWeight: 760
    lineHeight: 1.2
    letterSpacing: "0"
  title:
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 720
    lineHeight: 1.25
    letterSpacing: "0"
  body:
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "0.95rem"
    fontWeight: 400
    lineHeight: 1.55
    letterSpacing: "0"
  label:
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "0.82rem"
    fontWeight: 650
    lineHeight: 1.2
    letterSpacing: "0"
rounded:
  sm: "8px"
  pill: "999px"
spacing:
  xs: "0.35rem"
  sm: "0.62rem"
  md: "1rem"
  lg: "1.15rem"
  xl: "2rem"
components:
  button-primary:
    backgroundColor: "{colors.accent-blue}"
    textColor: "{colors.text}"
    rounded: "{rounded.sm}"
    padding: "0.5rem 1rem"
  button-secondary:
    backgroundColor: "transparent"
    textColor: "{colors.text}"
    rounded: "{rounded.sm}"
    padding: "0.5rem 1rem"
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text}"
    rounded: "{rounded.sm}"
    padding: "{spacing.lg}"
  chip-active:
    backgroundColor: "rgba(37, 99, 235, 0.14)"
    textColor: "{colors.text}"
    rounded: "{rounded.pill}"
    padding: "0.42rem 0.7rem"
---

# Design System: Kickways

## Overview

**Creative North Star: "The Career Command Center"**

Kickways uses a restrained, premium, evidence-led interface that makes career intelligence feel clear and usable. The system should feel closer to a focused SaaS dashboard than a football database: dark, calm, structured, and built around the next decision the player or agent needs to make.

The visual language is compact but breathable. Cards present destination evidence, stat rows summarize the signal, and blue appears as a rare action or active-state accent. The interface should support repeated comparison without becoming loud, decorative, or dashboard-heavy.

**Key Characteristics:**
- Dark neutral workspace with quiet tonal layering.
- One primary blue accent for action, active state, and emphasis.
- Compact intelligence cards with direct evidence and next-step CTAs.
- Rounded but disciplined SaaS controls using 8px corners.
- Plain-language metrics designed for players and agents, not analysts.

## Colors

The palette is a dark neutral SaaS system with a single confident blue accent.

### Primary
- **Career Blue**: Used for primary buttons, active journey steps, eyebrow labels, and selected-state emphasis.

### Neutral
- **Command Black**: Main app background; keeps the product focused and reduces visual noise.
- **Sidebar Graphite**: Sidebar background; slightly lifted from the main background to create stable navigation.
- **Panel Charcoal**: Primary surface for cards and metric containers.
- **Soft Panel Charcoal**: Secondary surface for quieter containers and tonal separation.
- **Signal White**: Main text color for headings and important values.
- **Soft Slate**: Secondary text and league labels.
- **Muted Slate**: Captions, evidence copy, labels, and helper text.
- **Hairline Slate**: Borders and dividers; defines structure without creating table-like clutter.

### Named Rules

**The One Accent Rule.** Blue is the only accent color. Do not introduce rainbow metric colors or separate semantic hues unless a real product state requires them.

**The Evidence First Rule.** Color supports hierarchy and action; it should not be used to make weak evidence feel stronger.

## Typography

**Display Font:** System UI stack.
**Body Font:** System UI stack.
**Label/Mono Font:** System UI stack; no separate mono system is established.

**Character:** Typography is modern, compact, and functional. Weight and spacing carry hierarchy instead of decorative font choices.

### Hierarchy
- **Display**: Heavy, large, tight page title for product headers and destination report titles.
- **Headline**: Strong country or destination names inside opportunity cards.
- **Title**: Section headers that introduce the next decision area.
- **Body**: Supporting copy, evidence sentences, and practical explanations.
- **Label**: Eyebrows, chips, metric labels, navigation, and compact controls.

### Named Rules

**The No Hero Inside Cards Rule.** Card headings stay compact. Hero-scale type belongs only to page-level headers.

**The Zero Letter-Spacing Rule.** Body, headline, and UI type use zero letter spacing. Uppercase eyebrow text may use restrained spacing only for product-level orientation.

## Layout

Kickways uses a centered Streamlit content column with a maximum width of 1180px and generous page padding. Pages are organized as a decision journey: a product header, journey steps, compact summary stats, then one primary section that asks the user to inspect or choose the next destination.

Destination opportunities use stacked cards rather than tables. Card internals use a simple vertical rhythm: country and league first, evidence sentence second, stat row third, CTA outside the evidence block when applicable.

Layouts should remain dense enough for scanning but never cramped. Use two-column layouts only when they clarify the task, such as an input form paired with a short explanation.

## Elevation & Depth

The system is flat by default and uses tonal layering, borders, and a tiny inset highlight for depth. Shadows are nearly absent; this keeps the app from feeling like a generic card dashboard.

### Shadow Vocabulary
- **Primary Card Inset**: A subtle inset top highlight used only for the strongest recommended opportunity.

### Named Rules

**The Flat Intelligence Rule.** Surfaces should feel structured, not floating. Prefer borders and tonal shifts over drop shadows.

## Shapes

The shape language is disciplined and SaaS-native. Buttons, cards, metrics, and inputs use 8px rounded corners. Pills are reserved for journey steps and compact state labels, using fully rounded corners.

Avoid nested cards and oversized rounded panels. The product should feel precise, not bubbly.

## Components

### Buttons
- **Shape:** Gently rounded rectangle (8px).
- **Primary:** Career Blue background with white text. Use for the one primary action on a screen.
- **Secondary:** Transparent or dark surface with Hairline Slate border. Use for inspection, navigation, and lower-priority actions.
- **Width:** Buttons should be content-sized unless they are the main form submission.

### Chips
- **Style:** Fully rounded, compact labels with muted text and a quiet border.
- **Active State:** Blue-tinted background and blue border.
- **Use:** Journey steps, compact context summaries, and selected filters. Do not use chips for non-clickable metric summaries when a stat row is clearer.

### Cards / Containers
- **Corner Style:** 8px radius.
- **Background:** Subtle vertical tonal gradient on opportunity cards.
- **Shadow Strategy:** Flat by default; a tiny inset highlight only for the primary recommendation.
- **Border:** Muted slate border for structure.
- **Internal Padding:** Approximately 1.15rem.

### Inputs / Fields
- **Style:** Streamlit-native controls shaped by the global 8px button/input language.
- **Focus:** Keep focus visible and aligned with Streamlit accessibility defaults.
- **Use:** Current country, current league, origin country, origin league, and profile filters should be direct and plain-language.

### Navigation

Sidebar navigation is dark, quiet, and functional. Labels should describe the career journey rather than analytics pages: career path, opportunity explorer, destination intelligence, and advanced research tools.

### Destination Opportunity Card

The signature card pattern presents country, league, comparable-player evidence, level movement stats, and a destination intelligence CTA. It should not look like a table row, and it should never lead with raw percentages before the user understands what moved.

## Do's and Don'ts

### Do:
- **Do** use Career Blue sparingly for primary action, active state, and orientation.
- **Do** present comparable players and level movement as decision evidence.
- **Do** keep card radii at 8px and reserve pills for compact state.
- **Do** keep CTAs clear, content-sized, and attached to a natural next step.
- **Do** preserve consistency between overview metrics and destination report metrics.

### Don't:
- **Don't** make Kickways feel like a raw database explorer.
- **Don't** use rainbow dashboards, oversized widgets, or decorative gradients.
- **Don't** place cards inside other cards.
- **Don't** make non-clickable metric labels look like buttons.
- **Don't** invent proof, testimonials, or external credibility claims the data does not support.
