# Humain Brand Identity

Who library serves, how should feel, what should never look like.

---

## Users

Internal Humain teams + external clients building on Humain platform. Library powers HUMAIN One (platform dashboard) and HUMAIN Chat (AI assistant interface), plus other Humain products. Users = professionals in government, enterprise, AI/data contexts. Need interfaces feeling trustworthy and modern — not flashy or experimental.

## Brand Personality

**Ambitious, Strategic, Transformative.**

Humain brand = company driving AI transformation for serious contexts (government, enterprise). Interface should feel like confident leader — not trend follower. Every component conveys competence + forward-thinking without sacrificing clarity.

- **Voice**: Direct, confident, precise. No filler, no hype.
- **Tone**: Professional warmth — approachable but never casual. Executive briefing, not startup pitch.
- **Emotion**: Trustworthy & modern. Users should feel tool built by people who understand their domain.

## Aesthetic Direction

- **Visual tone**: Clean, structured, purposeful. Generous whitespace with tight info density where needed (data tables, dashboards). Not minimal for minimalism's sake — every element earns its place.
- **Brand color**: Humain aqua (`--primary: #009688`) with the Air scale (`--air-*`) for tints — distinctive, not typical blue SaaS palette. Use strategically as accent, not everywhere.
- **Typography**: Inter — functional and readable. Library prioritizes clarity over typographic flair since design system consumed by many products.
- **Theme**: Light + dark modes, both first-class. Dark mode essential for HUMAIN Chat and AI contexts.
- **References**: HUMAIN One (platform), HUMAIN Chat (AI assistant)

## Anti-References

- Generic SaaS dashboards with cyan-on-dark glow effects
- AI-slop aesthetics (purple gradients, glassmorphism everywhere, bouncy animations)
- Government sites that look dated or bureaucratic

## Design Principles

1. **Trustworthy by default** — Components should look + feel solid. No decorative flourishes undermining credibility. Accessibility (WCAG AA) non-negotiable.

2. **Token-driven consistency** — Every color, spacing value, typographic choice from design token system. No hard-coded values. Ensures coherence across HUMAIN One, HUMAIN Chat, client products.

3. **Progressive enhancement** — Features degrade gracefully. Animations respect `prefers-reduced-motion`. Backdrop effects use `@supports` guards. SSR-safe by default.

4. **Density-aware** — Same components work in spacious marketing layouts and dense data dashboards. Container queries + responsive variants adapt to context, not just viewport.

5. **AI-native** — 27+ AI components are first-class citizens, not afterthoughts. Typing indicators, thinking loaders, message streams, code blocks as polished as buttons and forms.

## Accessibility Targets

- **Standard**: WCAG 2.1 AA compliance
- **Focus**: `focus-visible` indicators on all interactive elements
- **Motion**: All animations respect `prefers-reduced-motion`
- **Contrast**: Minimum 4.5:1 for text, 3:1 for UI components
- **Keyboard**: Full keyboard navigation support; no focus traps
