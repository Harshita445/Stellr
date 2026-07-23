# Constellation — Visual Design System

**Inspired by**: Linear, Apple, Discord, Arc Browser  
**Rejected vibes**: Google Classroom, Moodle, University ERP

---

## Brand Emotion

| Layer | Emotion | Execution |
|-------|---------|-----------|
| **Premium** | High-craft, bespoke, every pixel intentional | Tight alignment, generous whitespace, no visual clutter |
| **Calm** | Quiet confidence, never loud, never urgent | Dark surface, muted tones, soft transitions |
| **Magical** | Delightful surprises, feels alive | Glow effects, animated constellations, starry micro-interactions |
| **Night Sky** | Deep space, celestial | `#0B1020` background, star particles, radial glows |
| **Intelligent** | Anticipates needs, surfaces what matters | Predictive availability summaries, smart polling |
| **Social** | Warm connection, seeing others | Friend avatars with live glow indicators, constellation connections |
| **Alive** | Constant gentle motion, breathing UI | Subtle pulse on free status, constellation line animations, shimmer on load |

---

## Design Tokens

### Color Palette

```css
/* tailwind.config.ts — theme.extend.colors */

/* Surface — the night sky */
const colors = {
  space: {
    900: '#0B1020',   /* Deepest space — page background */
    800: '#0E1526',   /* Slightly lighter — secondary surfaces */
    700: '#141B34',   /* Card / surface background */
    600: '#1A2340',   /* Elevated surface — modals, dropdowns */
    500: '#22305C',   /* Border / divider — subtle separation */
    400: '#2D3D6B',   /* Hover state on surfaces */
    300: '#3B4F82',   /* Active / selected surface */
  },

  /* Primary — the guiding star */
  primary: {
    50:  '#F5F3FF',
    100: '#EDE9FE',
    200: '#DDD6FE',
    300: '#C4B5FD',
    400: '#A78BFA',
    500: '#8B5CF6',   /* Main primary — buttons, active states */
    600: '#7C3AED',   /* Hover */
    700: '#6D28D9',   /* Active */
    800: '#5B21B6',   /* Pressed */
    900: '#4C1D95',
  },

  /* Accent — starlight / connection */
  accent: {
    50:  '#F0F9FF',
    100: '#E0F2FE',
    200: '#BAE6FD',
    300: '#7DD3FC',
    400: '#38BDF8',   /* Main accent — links, secondary buttons */
    500: '#0EA5E9',   /* Hover */
    600: '#0284C7',   /* Active */
    700: '#0369A1',
  },

  /* Status — availability semantic */
  status: {
    available:  '#22C55E',   /* Free — star glow, badge */
    busy:       '#EF4444',   /* In class — badge, indicator */
    away:       '#F59E0B',   /* Between classes / warning */
    offline:    '#475569',   /* No data — greyed out */
  },

  /* Text */
  text: {
    primary:   '#F8FAFC',   /* High-emphasis */
    secondary: '#CBD5E1',   /* Medium-emphasis */
    muted:     '#64748B',   /* Low-emphasis, placeholder */
    inverse:   '#0B1020',   /* On colored backgrounds */
  },

  /* Glass — for glassmorphism effects */
  glass: {
    white:  'rgba(255, 255, 255, 0.04)',
    border: 'rgba(255, 255, 255, 0.08)',
    hover:  'rgba(255, 255, 255, 0.08)',
    active: 'rgba(255, 255, 255, 0.12)',
  },

  /* Glow — for star / constellation effects */
  glow: {
    star:     'rgba(139, 92, 246, 0.6)',   /* primary-500 at 60% */
    starDim:  'rgba(139, 92, 246, 0.2)',
    connect:  'rgba(56, 189, 248, 0.5)',   /* accent-400 at 50% */
    connectFull: 'rgba(56, 189, 248, 0.8)',
    available: 'rgba(34, 197, 94, 0.5)',   /* status.available at 50% */
    pulse:    'rgba(139, 92, 246, 0.3)',
  },
}
```

### Tailwind CSS Variable Registration

```css
/* globals.css — :root variables */

@layer base {
  :root {
    /* Surface */
    --color-space-900: #0B1020;
    --color-space-800: #0E1526;
    --color-space-700: #141B34;
    --color-space-600: #1A2340;
    --color-space-500: #22305C;
    --color-space-400: #2D3D6B;
    --color-space-300: #3B4F82;

    /* Primary */
    --color-primary-50:  #F5F3FF;
    --color-primary-100: #EDE9FE;
    --color-primary-200: #DDD6FE;
    --color-primary-300: #C4B5FD;
    --color-primary-400: #A78BFA;
    --color-primary-500: #8B5CF6;
    --color-primary-600: #7C3AED;
    --color-primary-700: #6D28D9;
    --color-primary-800: #5B21B6;
    --color-primary-900: #4C1D95;

    /* Accent */
    --color-accent-400: #38BDF8;
    --color-accent-500: #0EA5E9;

    /* Status */
    --color-available: #22C55E;
    --color-busy:      #EF4444;
    --color-away:      #F59E0B;
    --color-offline:   #475569;

    /* Text */
    --color-text-primary:   #F8FAFC;
    --color-text-secondary: #CBD5E1;
    --color-text-muted:     #64748B;

    /* Glass */
    --glass-white:  rgba(255, 255, 255, 0.04);
    --glass-border: rgba(255, 255, 255, 0.08);
    --glass-hover:  rgba(255, 255, 255, 0.08);

    /* Glow */
    --glow-star:     rgba(139, 92, 246, 0.6);
    --glow-star-dim: rgba(139, 92, 246, 0.2);
    --glow-connect:  rgba(56, 189, 248, 0.5);
    --glow-available: rgba(34, 197, 94, 0.5);
  }
}
```

---

## Typography

### Font Family

```css
/* Primary: Inter for UI, system mono for code */

--font-sans:  'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono:  'JetBrains Mono', 'SF Mono', 'Fira Code', monospace;
```

### Type Scale

```css
--text-xs:     0.75rem;   /* 12px — labels, timestamps */
--text-sm:     0.875rem;  /* 14px — body, descriptions */
--text-base:   1rem;      /* 16px — default body */
--text-lg:     1.125rem;  /* 18px — large body */
--text-xl:     1.25rem;   /* 20px — section titles */
--text-2xl:    1.5rem;    /* 24px — card titles */
--text-3xl:    1.875rem;  /* 30px — page titles */
--text-4xl:    2.25rem;   /* 36px — hero */
--text-5xl:    3rem;      /* 48px — display */
```

### Font Weight

```css
--font-normal:    400;
--font-medium:    500;
--font-semibold:  600;
--font-bold:      700;
```

### Line Height

```css
--leading-tight:    1.25;
--leading-snug:     1.375;
--leading-normal:   1.5;
--leading-relaxed:  1.625;
```

### Letter Spacing

```css
--tracking-tight:   -0.025em;
--tracking-normal:  0;
--tracking-wide:    0.025em;
```

### Typography Usage

| Element | Size | Weight | Line Height | Letter Spacing | Class |
|---------|------|--------|-------------|----------------|-------|
| Page title | `text-3xl` | `bold` | `tight` | `tight` | `font-bold text-3xl leading-tight tracking-tight` |
| Section header | `text-xl` | `semibold` | `snug` | `tight` | `font-semibold text-xl leading-snug tracking-tight` |
| Card title | `text-lg` | `semibold` | `snug` | `normal` | `font-semibold text-lg leading-snug` |
| Body | `text-sm` | `normal` | `normal` | `normal` | `text-sm leading-normal` |
| Caption | `text-xs` | `medium` | `normal` | `wide` | `font-medium text-xs leading-normal tracking-wide` |
| Badge | `text-xs` | `semibold` | `tight` | `wide` | `font-semibold text-xs leading-tight tracking-wide` |
| Button label | `text-sm` | `semibold` | `snug` | `normal` | `font-semibold text-sm leading-snug` |
| Input label | `text-xs` | `medium` | `tight` | `wide` | `font-medium text-xs leading-tight tracking-wide uppercase` |
| Timestamp | `text-xs` | `normal` | `normal` | `normal` | `text-xs` |
| Friend name | `text-sm` | `medium` | `snug` | `normal` | `font-medium text-sm leading-snug` |
| Group name | `text-base` | `semibold` | `snug` | `tight` | `font-semibold text-base leading-snug tracking-tight` |
| Time slot | `text-sm` | `medium` | `tight` | `tight` | `font-medium text-sm leading-tight tracking-tight` |
| Constellation label | `text-2xl` | `bold` | `tight` | `tight` | `font-bold text-2xl leading-tight tracking-tight` |

---

## Spacing System

### Base Unit: 4px

```css
--spacing-px:  1px;
--spacing-0:   0px;
--spacing-0.5: 0.125rem;  /* 2px */
--spacing-1:   0.25rem;   /* 4px */
--spacing-1.5: 0.375rem;  /* 6px */
--spacing-2:   0.5rem;    /* 8px */
--spacing-2.5: 0.625rem;  /* 10px */
--spacing-3:   0.75rem;   /* 12px */
--spacing-3.5: 0.875rem;  /* 14px */
--spacing-4:   1rem;      /* 16px */
--spacing-5:   1.25rem;   /* 20px */
--spacing-6:   1.5rem;    /* 24px */
--spacing-7:   1.75rem;   /* 28px */
--spacing-8:   2rem;      /* 32px */
--spacing-9:   2.25rem;   /* 36px */
--spacing-10:  2.5rem;    /* 40px */
--spacing-11:  2.75rem;   /* 44px */
--spacing-12:  3rem;      /* 48px */
--spacing-14:  3.5rem;    /* 56px */
--spacing-16:  4rem;      /* 64px */
--spacing-20:  5rem;      /* 80px */
--spacing-24:  6rem;      /* 96px */
```

### Spacing Conventions

| Context | Token | Example |
|---------|-------|---------|
| Page edge padding | `px-6 md:px-10` | 24px mobile, 40px desktop |
| Between card groups | `space-y-6` | 24px |
| Inside card padding | `p-5` | 20px |
| Card header to body | `space-y-3` | 12px |
| Between list items | `space-y-2` | 8px |
| Between icon and label | `gap-2` | 8px |
| Button horizontal padding | `px-4` | 16px |
| Button height | `h-9` (sm), `h-10` (md), `h-11` (lg) | 36px / 40px / 44px |
| Input padding | `px-3 py-2` | 12px horizontal, 8px vertical |
| Modal padding | `p-6` | 24px |
| Modal from edge | `mx-4` | 16px |
| Section title from content | `mb-4` | 16px |
| Between label and input | `space-y-1.5` | 6px |

---

## Grid System

```css
/* 12-column responsive grid */

/* Container */
.container {
  @apply mx-auto px-6 md:px-10;
  max-width: 1280px;
}

/* Dashboard layout — 3-column */
.dashboard-grid {
  display: grid;
  grid-template-columns: 260px 1fr 320px;
  gap: 24px;
}

/* Friend list — 2-column responsive */
.friend-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

/* Group grid — responsive cards */
.group-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
}
```

### Breakpoints

| Name | Width | Usage |
|------|-------|-------|
| `sm` | 640px | Mobile landscape |
| `md` | 768px | Tablet |
| `lg` | 1024px | Desktop |
| `xl` | 1280px | Large desktop |
| `2xl` | 1536px | Wide |

---

## Radius System

```css
--radius-none:    0px;
--radius-sm:      0.25rem;   /* 4px — small labels, avatars */
--radius-md:      0.5rem;    /* 8px — cards, inputs */
--radius-lg:      0.75rem;   /* 12px — modals, dropdowns */
--radius-xl:      1rem;      /* 16px — sheets, drawers */
--radius-2xl:     1.5rem;    /* 24px — large modals */
--radius-3xl:     2rem;      /* 32px — special emphasis */
--radius-full:    9999px;    /* pills, badges, avatars */
```

### Radius Usage

| Component | Radius |
|-----------|--------|
| Button | `md` (8px) |
| Card | `lg` (12px) |
| Modal | `xl` (16px) |
| Input field | `md` (8px) |
| Badge | `full` (pill) |
| Avatar (small) | `full` (circle) |
| Tooltip | `md` (8px) |
| Dropdown menu | `lg` (12px) |
| Alert | `lg` (12px) |
| Skeleton | `md` (8px) |
| Search bar | `full` (pill) |
| Constellation star | `full` (circle) |

---

## Elevation System

```css
/* z-index layers */
--z-dropdown:       100;
--z-sticky:         200;
--z-navbar:         300;
--z-sidebar:        400;
--z-backdrop:       500;
--z-modal:          600;
--z-popover:        700;
--z-tooltip:        800;
--z-toast:          900;
```

---

## Shadows

```css
--shadow-xs:   0 1px 2px rgba(0, 0, 0, 0.3);
--shadow-sm:   0 1px 3px rgba(0, 0, 0, 0.35), 0 1px 2px rgba(0, 0, 0, 0.25);
--shadow-md:   0 4px 6px rgba(0, 0, 0, 0.4), 0 2px 4px rgba(0, 0, 0, 0.3);
--shadow-lg:   0 10px 15px rgba(0, 0, 0, 0.45), 0 4px 6px rgba(0, 0, 0, 0.3);
--shadow-xl:   0 20px 25px rgba(0, 0, 0, 0.5), 0 10px 10px rgba(0, 0, 0, 0.3);
--shadow-2xl:  0 25px 50px rgba(0, 0, 0, 0.55);

/* Glow shadows — for status indicators and constellation */
--shadow-glow-sm:     0 0 8px var(--glow-star);
--shadow-glow-md:     0 0 16px var(--glow-star);
--shadow-glow-lg:     0 0 32px var(--glow-star);
--shadow-glow-available: 0 0 12px var(--glow-available);
--shadow-glow-connect:    0 0 20px var(--glow-connect);
--shadow-glow-connect-full: 0 0 30px var(--glow-connect);
```

### Shadow Usage

| Component | Shadow |
|-----------|--------|
| Card (resting) | `sm` |
| Card (hovered) | `md` |
| Modal | `xl` |
| Dropdown | `lg` |
| Toast | `lg` |
| Context menu | `lg` |
| Sticky header | `md` (bottom only) |
| Star (free) | `glow-available` |
| Star (connected) | `glow-connect` |
| Constellation (all free) | `glow-connect-full` |

---

## Motion System

### Duration Tokens

```css
--duration-instant:  0ms;
--duration-fast:     100ms;
--duration-normal:   200ms;
--duration-slow:     300ms;
--duration-slug:     500ms;
--duration-snail:    800ms;
```

### Easing Tokens

```css
/* Linear-inspired custom easings */
--ease-out:     cubic-bezier(0.16, 1, 0.3, 1);       /* Deceleration — things entering */
--ease-in:      cubic-bezier(0.4, 0, 0.68, 0.06);     /* Acceleration — things leaving */
--ease-in-out:  cubic-bezier(0.65, 0, 0.35, 1);       /* Symmetric */
--ease-spring:  cubic-bezier(0.34, 1.56, 0.64, 1);    /* Spring-like pop */
--ease-smooth:  cubic-bezier(0.4, 0, 0.2, 1);         /* Standard Material */
```

### Motion Patterns

```css
/* Fade in */
@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}

/* Slide up + fade */
@keyframes slideUp {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Slide down + fade */
@keyframes slideDown {
  from { opacity: 0; transform: translateY(-8px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Scale in (modal, popover) */
@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to   { opacity: 1; transform: scale(1); }
}

/* Pulse (free star glow) */
@keyframes pulseGlow {
  0%, 100% { box-shadow: 0 0 8px var(--glow-available); }
  50%      { box-shadow: 0 0 20px var(--glow-available), 0 0 40px var(--glow-available); }
}

/* Constellation pulse (all free) */
@keyframes constellationPulse {
  0%, 100% { opacity: 1; filter: brightness(1); }
  50%      { opacity: 0.8; filter: brightness(1.2); }
}

/* Shimmer (loading) */
@keyframes shimmer {
  0%   { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

/* Connection line draw */
@keyframes drawLine {
  from { stroke-dashoffset: 1000; }
  to   { stroke-dashoffset: 0; }
}

/* Star twinkle */
@keyframes twinkle {
  0%, 100% { opacity: 0.6; transform: scale(0.9); }
  50%      { opacity: 1; transform: scale(1.1); }
}

/* Breathing background */
@keyframes breathe {
  0%, 100% { opacity: 0.03; }
  50%      { opacity: 0.06; }
}
```

### Motion Conventions

| Interaction | Duration | Easing | Animation |
|-------------|----------|--------|-----------|
| Page enter | 300ms | `ease-out` | `slideUp` with stagger on children (50ms delay each) |
| Modal open | 200ms | `ease-spring` | `scaleIn` + backdrop fade |
| Modal close | 150ms | `ease-in` | Reverse scale + fade |
| Dropdown open | 150ms | `ease-out` | `slideDown` |
| Hover (card) | 200ms | `ease-out` | TranslateY(-2px) + shadow `sm` → `md` |
| Hover (button) | 100ms | `ease-out` | Background + shadow transition |
| Click / tap | 100ms | `ease-out` | Scale(0.97) |
| Friend status change | 500ms | `ease-out` | Opacity + glow transition |
| Constellation line draw | 800ms | `ease-smooth` | `drawLine` stroke animation |
| Star pulse (free) | 2000ms | ease-in-out | `pulseGlow` infinite |
| All free pulse | 3000ms | ease-in-out | `constellationPulse` infinite |
| Skeleton | 1500ms | linear | `shimmer` infinite |
| Toast enter | 300ms | `ease-spring` | `slideUp` |
| List item enter | 200ms | `ease-out` | `slideUp` (stagger 30ms) |

---

## Glass Effects

```css
/* Base glass surface */
.glass {
  background: var(--glass-white);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
}

/* Stronger glass (modals, sheets) */
.glass-strong {
  background: rgba(20, 27, 52, 0.8);  /* space-700 at 80% */
  backdrop-filter: blur(32px);
  -webkit-backdrop-filter: blur(32px);
  border: 1px solid var(--glass-border);
}

/* Glass hover */
.glass-hover:hover {
  background: var(--glass-hover);
}

/* Glass active */
.glass-active:active {
  background: var(--glass-active);
}
```

### Glass Usage

| Component | Variant | Why |
|-----------|---------|-----|
| Navigation sidebar | `glass` | Stays visible over content, depth without heaviness |
| Modal | `glass-strong` | Focus on modal content, blurred backdrop |
| Dropdown menu | `glass-strong` | Floats above everything, needs legibility |
| Sheet / drawer | `glass-strong` | Same as modal |
| Context menu | `glass-strong` | Same as dropdown |
| Sticky header | `glass` | Subtle, doesn't fight content |

---

## Glow Effects

```css
/* Star glow when free */
.glow-available {
  box-shadow:
    0 0 8px var(--glow-available),
    0 0 16px var(--glow-available);
}

/* Connection glow */
.glow-connect {
  filter: drop-shadow(0 0 4px var(--glow-connect));
}

/* Primary glow — hover states, active elements */
.glow-primary {
  box-shadow: 0 0 12px var(--glow-star);
}

/* Full constellation pulse */
.glow-constellation {
  animation: constellationPulse 3s ease-in-out infinite;
  filter: drop-shadow(0 0 20px var(--glow-connect-full));
}
```

### Glow Usage

| Element | Effect | When |
|---------|--------|------|
| Star node (free) | `glow-available` with `pulseGlow` | User is free |
| Star node (busy) | None — rendered in muted `space-400` | User is in class |
| Star node (offline) | Opacity 0.3 | No data |
| Connection line | `glow-connect` + `drawLine` | Both users free |
| Constellation container | `glow-constellation` | All members free |
| Button (primary hover) | `glow-primary` | Hover state |
| Active indicator | Pulsing `glow-available` | Live status |

---

## Gradients

```css
/* Page background gradient — subtle cosmic drift */
.bg-cosmic {
  background:
    radial-gradient(ellipse at 20% 50%, rgba(139, 92, 246, 0.06) 0%, transparent 60%),
    radial-gradient(ellipse at 80% 20%, rgba(56, 189, 248, 0.04) 0%, transparent 50%),
    var(--color-space-900);
}

/* Card gradient — subtle elevation */
.bg-card-gradient {
  background: linear-gradient(
    180deg,
    rgba(255, 255, 255, 0.04) 0%,
    transparent 100%
  );
}

/* Primary gradient — buttons, highlights */
.bg-primary-gradient {
  background: linear-gradient(
    135deg,
    var(--color-primary-500) 0%,
    var(--color-primary-600) 100%
  );
}

/* Accent gradient */
.bg-accent-gradient {
  background: linear-gradient(
    135deg,
    var(--color-accent-400) 0%,
    var(--color-accent-500) 100%
  );
}

/* Status glow radial */
.bg-status-available {
  background: radial-gradient(
    circle,
    rgba(34, 197, 94, 0.15) 0%,
    transparent 70%
  );
}

/* Constellation background — per-group subtle nebula */
.bg-nebula {
  background: radial-gradient(
    circle at center,
    rgba(139, 92, 246, 0.08) 0%,
    transparent 70%
  );
}
```

---

## Component Design Specifications

---

### Button Variants

```css
/* Base button */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  border-radius: var(--radius-md);
  font-weight: var(--font-semibold);
  font-size: var(--text-sm);
  line-height: var(--leading-snug);
  transition: all var(--duration-fast) var(--ease-out);
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}

/* Sizes */
.btn-sm  { height: 32px; padding: 0 12px; font-size: var(--text-xs); }
.btn-md  { height: 40px; padding: 0 16px; }
.btn-lg  { height: 48px; padding: 0 24px; font-size: var(--text-base); }
.btn-icon { height: 40px; width: 40px; padding: 0; }

/* Primary — filled */
.btn-primary {
  background: var(--color-primary-500);
  color: white;
}
.btn-primary:hover {
  background: var(--color-primary-600);
  box-shadow: var(--shadow-glow-sm);
}
.btn-primary:active {
  background: var(--color-primary-700);
  transform: scale(0.97);
}
.btn-primary:disabled {
  background: var(--color-space-500);
  color: var(--color-text-muted);
  cursor: not-allowed;
  box-shadow: none;
}

/* Secondary — ghost on glass */
.btn-secondary {
  background: transparent;
  color: var(--color-text-primary);
  border: 1px solid var(--glass-border);
}
.btn-secondary:hover {
  background: var(--glass-hover);
  border-color: var(--color-space-400);
}
.btn-secondary:active {
  background: var(--glass-active);
  transform: scale(0.97);
}

/* Tertiary — text only */
.btn-tertiary {
  background: transparent;
  color: var(--color-text-secondary);
}
.btn-tertiary:hover {
  color: var(--color-text-primary);
  background: var(--glass-white);
}
.btn-tertiary:active {
  background: var(--glass-hover);
}

/* Danger */
.btn-danger {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-busy);
  border: 1px solid rgba(239, 68, 68, 0.2);
}
.btn-danger:hover {
  background: rgba(239, 68, 68, 0.2);
}
.btn-danger:active {
  background: rgba(239, 68, 68, 0.3);
}

/* Ghost — icon button */
.btn-ghost {
  background: transparent;
  color: var(--color-text-muted);
}
.btn-ghost:hover {
  background: var(--glass-white);
  color: var(--color-text-primary);
}
.btn-ghost:active {
  background: var(--glass-hover);
}
```

---

### Cards

```css
/* Base card */
.card {
  background: var(--color-space-700);
  border-radius: var(--radius-lg);
  border: 1px solid var(--glass-border);
  padding: var(--spacing-5);
  transition: all var(--duration-normal) var(--ease-out);
}

/* Interactive card (clickable) */
.card-interactive {
  @extend .card;
  cursor: pointer;
}
.card-interactive:hover {
  border-color: var(--color-space-400);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}
.card-interactive:active {
  transform: translateY(0);
}

/* Glass card (for overlays, panels) */
.card-glass {
  @extend .card;
  background: var(--glass-white);
  backdrop-filter: blur(20px);
}

/* Card with glow (featured group, current status) */
.card-glow {
  @extend .card;
  border-color: rgba(139, 92, 246, 0.2);
  box-shadow: 0 0 20px rgba(139, 92, 246, 0.06);
}

/* Card sections */
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-3);
}

.card-body {
  /* Natural flow */
}

.card-footer {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  margin-top: var(--spacing-4);
  padding-top: var(--spacing-4);
  border-top: 1px solid var(--glass-border);
}
```

---

### Badges

```css
/* Base badge */
.badge {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-1);
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  line-height: var(--leading-tight);
  letter-spacing: var(--tracking-wide);
  text-transform: uppercase;
}

/* Variants */
.badge-available {
  background: rgba(34, 197, 94, 0.1);
  color: var(--color-available);
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.badge-busy {
  background: rgba(239, 68, 68, 0.1);
  color: var(--color-busy);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.badge-away {
  background: rgba(245, 158, 11, 0.1);
  color: var(--color-away);
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.badge-primary {
  background: rgba(139, 92, 246, 0.1);
  color: var(--color-primary-400);
  border: 1px solid rgba(139, 92, 246, 0.2);
}

.badge-neutral {
  background: var(--glass-white);
  color: var(--color-text-muted);
  border: 1px solid var(--glass-border);
}

/* Dot indicator — smaller, no text */
.badge-dot {
  width: 8px;
  height: 8px;
  border-radius: var(--radius-full);
  padding: 0;
}
.badge-dot-available { background: var(--color-available); box-shadow: 0 0 6px var(--glow-available); }
.badge-dot-busy      { background: var(--color-busy); }
.badge-dot-away      { background: var(--color-away); }
.badge-dot-offline   { background: var(--color-offline); }
```

---

### Alerts

```css
/* Alert base */
.alert {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-3);
  padding: var(--spacing-4);
  border-radius: var(--radius-lg);
  border: 1px solid;
  font-size: var(--text-sm);
  line-height: var(--leading-normal);
}

/* Variants */
.alert-info {
  background: rgba(56, 189, 248, 0.06);
  border-color: rgba(56, 189, 248, 0.15);
  color: var(--color-accent-400);
}

.alert-success {
  background: rgba(34, 197, 94, 0.06);
  border-color: rgba(34, 197, 94, 0.15);
  color: var(--color-available);
}

.alert-warning {
  background: rgba(245, 158, 11, 0.06);
  border-color: rgba(245, 158, 11, 0.15);
  color: var(--color-away);
}

.alert-error {
  background: rgba(239, 68, 68, 0.06);
  border-color: rgba(239, 68, 68, 0.15);
  color: var(--color-busy);
}

/* Atomic parts */
.alert-icon {
  flex-shrink: 0;
  width: 18px;
  height: 18px;
  margin-top: 1px;
}
.alert-content { flex: 1; }
.alert-title {
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  margin-bottom: 2px;
}
.alert-description {
  color: var(--color-text-secondary);
}
.alert-dismiss {
  flex-shrink: 0;
  color: var(--color-text-muted);
  cursor: pointer;
}
.alert-dismiss:hover {
  color: var(--color-text-primary);
}
```

---

### Tooltips

```css
/* Tooltip wrapper */
.tooltip-trigger {
  position: relative;
  cursor: pointer;
}

/* Tooltip content */
.tooltip {
  position: absolute;
  z-index: var(--z-tooltip);
  padding: 6px 10px;
  border-radius: var(--radius-md);
  background: var(--color-space-600);
  border: 1px solid var(--glass-border);
  box-shadow: var(--shadow-lg);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  color: var(--color-text-primary);
  line-height: var(--leading-tight);
  white-space: nowrap;
  pointer-events: none;
  opacity: 0;
  transform: translateY(4px);
  transition: all var(--duration-fast) var(--ease-out);
}

.tooltip-trigger:hover .tooltip {
  opacity: 1;
  transform: translateY(0);
}

/* Positioning */
.tooltip-top    { bottom: calc(100% + 6px); left: 50%; transform: translateX(-50%) translateY(4px); }
.tooltip-bottom { top: calc(100% + 6px); left: 50%; transform: translateX(-50%) translateY(-4px); }
.tooltip-left   { right: calc(100% + 6px); top: 50%; transform: translateY(-50%) translateX(4px); }
.tooltip-right  { left: calc(100% + 6px); top: 50%; transform: translateY(-50%) translateX(-4px); }

/* Show on hover */
.tooltip-trigger:hover .tooltip-top,
.tooltip-trigger:hover .tooltip-bottom,
.tooltip-trigger:hover .tooltip-left,
.tooltip-trigger:hover .tooltip-right {
  transform: translateX(-50%) translateY(0);
}

/* Arrow */
.tooltip::after {
  content: '';
  position: absolute;
  width: 6px;
  height: 6px;
  background: var(--color-space-600);
  border: 1px solid var(--glass-border);
  transform: rotate(45deg);
}
.tooltip-top::after {
  bottom: -4px;
  left: 50%;
  margin-left: -3px;
  border-top: none;
  border-left: none;
}
```

---

### Skeletons

```css
/* Skeleton base */
.skeleton {
  background: linear-gradient(
    90deg,
    var(--color-space-600) 25%,
    var(--color-space-400) 50%,
    var(--color-space-600) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s ease-in-out infinite;
  border-radius: var(--radius-md);
}

/* Variants */
.skeleton-text      { height: 14px; width: 100%; }
.skeleton-title     { height: 20px; width: 60%; }
.skeleton-avatar    { width: 40px; height: 40px; border-radius: var(--radius-full); }
.skeleton-avatar-sm { width: 32px; height: 32px; border-radius: var(--radius-full); }
.skeleton-card      { height: 120px; width: 100%; border-radius: var(--radius-lg); }
.skeleton-button    { height: 40px; width: 100px; border-radius: var(--radius-md); }
.skeleton-badge     { height: 20px; width: 60px; border-radius: var(--radius-full); }
```

---

### Empty States

```css
/* Empty state container */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-16) var(--spacing-6);
  text-align: center;
  gap: var(--spacing-4);
}

/* Constellation illustration variants */
.empty-state-icon {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-full);
  background: var(--glass-white);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
}

.empty-state-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  line-height: var(--leading-snug);
}

.empty-state-description {
  font-size: var(--text-sm);
  color: var(--color-text-muted);
  max-width: 320px;
  line-height: var(--leading-normal);
}

.empty-state-action {
  margin-top: var(--spacing-2);
}
```

### Empty State Copy Patterns

| Context | Title | Description | Action |
|---------|-------|-------------|--------|
| No friends | No stars in your sky yet | Add friends by searching their roll number to start connecting | Search friends |
| No groups | No constellations yet | Create a group with your friends to see your constellations | Create group |
| No timetable | No schedule imported | Wait for your admin to upload this semester's timetable | (hidden) |
| No availability | No data for today | Your timetable doesn't have any entries scheduled for today | (none) |
| No search results | No stars found | Try a different roll number or name | (none) |
| No notifications | All quiet in the cosmos | You'll see notifications here when friends are free | (none) |
| No mutual free time | No common slots today | Your schedules don't overlap today — check another day | View another day |

---

### Loading States

```css
/* Full page loading */
.page-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}

/* Inline loading */
.inline-loading {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-8);
  justify-content: center;
  color: var(--color-text-muted);
  font-size: var(--text-sm);
}

/* Star spinner — custom constellation spinner */
.spinner-star {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-full);
  background: var(--color-primary-500);
  box-shadow: var(--shadow-glow-md);
  animation: pulseGlow 1.5s ease-in-out infinite;
}

/* Skeleton page layout */
.skeleton-page {
  display: grid;
  gap: var(--spacing-6);
  padding: var(--spacing-6);
}
.skeleton-page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.skeleton-page-content {
  display: grid;
  gap: var(--spacing-4);
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
}
```

---

### Navigation

```css
/* Sidebar — primary navigation */
.sidebar {
  width: 260px;
  height: 100vh;
  position: fixed;
  top: 0;
  left: 0;
  display: flex;
  flex-direction: column;
  padding: var(--spacing-6);
  background: var(--glass-white);
  backdrop-filter: blur(20px);
  border-right: 1px solid var(--glass-border);
  z-index: var(--z-sidebar);
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding-bottom: var(--spacing-8);
  margin-bottom: var(--spacing-6);
  border-bottom: 1px solid var(--glass-border);
}

.sidebar-brand {
  font-size: var(--text-xl);
  font-weight: var(--font-bold);
  color: var(--color-text-primary);
  letter-spacing: var(--tracking-tight);
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

/* Nav items */
.nav-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
  transition: all var(--duration-fast) var(--ease-out);
  cursor: pointer;
  text-decoration: none;
}

.nav-item:hover {
  background: var(--glass-hover);
  color: var(--color-text-primary);
}

.nav-item-active {
  background: rgba(139, 92, 246, 0.1);
  color: var(--color-primary-400);
}

.nav-item-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.nav-section-label {
  font-size: var(--text-xs);
  font-weight: var(--font-semibold);
  color: var(--color-text-muted);
  letter-spacing: var(--tracking-wide);
  text-transform: uppercase;
  padding: var(--spacing-4) var(--spacing-3) var(--spacing-2);
}

/* Bottom tab bar (mobile) */
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: var(--glass-strong);
  backdrop-filter: blur(20px);
  border-top: 1px solid var(--glass-border);
  display: flex;
  align-items: center;
  justify-content: space-around;
  z-index: var(--z-navbar);
  padding: 0 var(--spacing-4);
}

.bottom-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  color: var(--color-text-muted);
  font-size: 10px;
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: color var(--duration-fast) var(--ease-out);
}
.bottom-nav-item:hover { color: var(--color-text-secondary); }
.bottom-nav-item-active { color: var(--color-primary-400); }

.bottom-nav-icon {
  width: 24px;
  height: 24px;
}
```

---

### Modals

```css
/* Backdrop */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(8px);
  z-index: var(--z-backdrop);
  animation: fadeIn var(--duration-normal) var(--ease-out);
}

/* Modal container */
.modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: var(--z-modal);
  width: 100%;
  max-width: 480px;
  margin: 0 var(--spacing-4);
  animation: scaleIn var(--duration-normal) var(--ease-spring);
}

.modal-content {
  background: var(--color-space-600);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  padding: var(--spacing-6);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-5);
}

.modal-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  letter-spacing: var(--tracking-tight);
}

.modal-close {
  color: var(--color-text-muted);
  cursor: pointer;
  border-radius: var(--radius-md);
  padding: var(--spacing-1);
  transition: all var(--duration-fast) var(--ease-out);
}
.modal-close:hover {
  color: var(--color-text-primary);
  background: var(--glass-hover);
}

.modal-body {
  /* Natural flow for form content */
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--spacing-3);
  margin-top: var(--spacing-6);
  padding-top: var(--spacing-5);
  border-top: 1px solid var(--glass-border);
}
```

---

### Search Components

```css
/* Search bar */
.search-bar {
  position: relative;
  width: 100%;
}

.search-input {
  width: 100%;
  height: 44px;
  padding: 0 var(--spacing-10) 0 var(--spacing-4);
  background: var(--color-space-700);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-full);
  color: var(--color-text-primary);
  font-size: var(--text-sm);
  transition: all var(--duration-normal) var(--ease-out);
  outline: none;
}

.search-input::placeholder {
  color: var(--color-text-muted);
}

.search-input:focus {
  border-color: rgba(139, 92, 246, 0.3);
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
  background: var(--color-space-600);
}

.search-icon {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-muted);
  width: 18px;
  height: 18px;
  pointer-events: none;
}

/* Search results dropdown */
.search-results {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: var(--color-space-600);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  max-height: 320px;
  overflow-y: auto;
  z-index: var(--z-dropdown);
  animation: slideDown var(--duration-fast) var(--ease-out);
}

.search-result-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-3) var(--spacing-4);
  cursor: pointer;
  transition: background var(--duration-fast) var(--ease-out);
}
.search-result-item:hover {
  background: var(--glass-hover);
}
.search-result-item:first-child {
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}
.search-result-item:last-child {
  border-radius: 0 0 var(--radius-lg) var(--radius-lg);
}

.search-result-empty {
  padding: var(--spacing-8) var(--spacing-4);
  text-align: center;
  color: var(--color-text-muted);
  font-size: var(--text-sm);
}
```

---

### Group Components

```css
/* Group card (list view) */
.group-card {
  @extend .card-interactive;
}

.group-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.group-card-name {
  font-size: var(--text-base);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
}

.group-card-meta {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  margin-top: var(--spacing-1);
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

/* Constellation preview inside group card */
.group-card-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-6);
  min-height: 100px;
}

/* Group detail page header */
.group-detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-6);
}

.group-status-badge {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

/* Member list */
.member-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
}

.member-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--radius-md);
  transition: background var(--duration-fast) var(--ease-out);
}
.member-row:hover {
  background: var(--glass-white);
}

.member-avatar {
  position: relative;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-full);
  background: var(--color-space-500);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-sm);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  flex-shrink: 0;
}

.member-avatar-status {
  position: absolute;
  bottom: -1px;
  right: -1px;
  width: 10px;
  height: 10px;
  border-radius: var(--radius-full);
  border: 2px solid var(--color-space-700);
}

.member-info {
  flex: 1;
  min-width: 0;
}

.member-name {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.member-status {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
}

.member-actions {
  flex-shrink: 0;
}
```

---

### Friend Components

```css
/* Friend card */
.friend-card {
  @extend .card-interactive;
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
}

.friend-avatar {
  position: relative;
  width: 44px;
  height: 44px;
  border-radius: var(--radius-full);
  background: var(--color-space-500);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
  flex-shrink: 0;
  transition: box-shadow var(--duration-normal) var(--ease-out);
}

.friend-avatar.free {
  box-shadow: 0 0 0 2px var(--color-available);
}

.friend-avatar .status-ring {
  position: absolute;
  inset: -2px;
  border-radius: var(--radius-full);
  border: 2px solid transparent;
}
.friend-avatar.free .status-ring { border-color: var(--color-available); }
.friend-avatar.busy .status-ring { border-color: var(--color-busy); }

.friend-info {
  flex: 1;
  min-width: 0;
}

.friend-name {
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  color: var(--color-text-primary);
}

.friend-detail {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin-top: 1px;
}

.friend-status {
  flex-shrink: 0;
}

/* Friend comparison view */
.comparison-timeline {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
  padding: var(--spacing-4) 0;
}

.comparison-row {
  display: grid;
  grid-template-columns: 100px 1fr;
  align-items: center;
  gap: var(--spacing-3);
}

.comparison-label {
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
  text-align: right;
}

.comparison-bar {
  height: 24px;
  border-radius: var(--radius-md);
  position: relative;
  overflow: hidden;
}

.comparison-bar-busy {
  background: var(--color-space-500);
}

.comparison-bar-free {
  background: rgba(34, 197, 94, 0.15);
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.comparison-bar-overlap {
  background: rgba(139, 92, 246, 0.2);
  border: 1px solid rgba(139, 92, 246, 0.3);
}
```

---

### Availability Components

```css
/* Current status card — dashboard hero */
.current-status-card {
  @extend .card-glow;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
  position: relative;
  overflow: hidden;
}

.current-status-card::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(34, 197, 94, 0.06) 0%, transparent 70%);
  pointer-events: none;
}

.current-status-indicator {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: var(--radius-full);
  transition: all var(--duration-slow) var(--ease-out);
}
.status-dot.free { background: var(--color-available); box-shadow: 0 0 12px var(--glow-available); animation: pulseGlow 2s ease-in-out infinite; }
.status-dot.busy { background: var(--color-busy); }
.status-dot.away { background: var(--color-away); }

.status-label {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--color-text-primary);
}

.status-time {
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}

/* Schedule timeline */
.schedule-timeline {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
  position: relative;
}

.schedule-slot {
  display: grid;
  grid-template-columns: 60px 1fr;
  gap: var(--spacing-3);
  padding: var(--spacing-2) 0;
  align-items: center;
}

.schedule-time {
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  color: var(--color-text-muted);
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.schedule-event {
  padding: var(--spacing-2) var(--spacing-3);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  transition: all var(--duration-fast) var(--ease-out);
}

.schedule-event-lecture {
  background: rgba(139, 92, 246, 0.08);
  border-left: 3px solid var(--color-primary-500);
}

.schedule-event-lab {
  background: rgba(56, 189, 248, 0.08);
  border-left: 3px solid var(--color-accent-400);
}

.schedule-event-tutorial {
  background: rgba(245, 158, 11, 0.08);
  border-left: 3px solid var(--color-away);
}

.schedule-event-free {
  /* Empty space, no rendering */
}

.schedule-event-name {
  font-weight: var(--font-medium);
  color: var(--color-text-primary);
}

.schedule-event-detail {
  font-size: var(--text-xs);
  color: var(--color-text-muted);
  margin-top: 1px;
}

/* Current class highlight */
.schedule-event-current {
  border-color: var(--color-available);
  box-shadow: 0 0 0 1px rgba(34, 197, 94, 0.2);
}

/* Next event label */
.schedule-event-next {
  position: relative;
}
.schedule-event-next::after {
  content: 'NEXT';
  position: absolute;
  top: -6px;
  right: 8px;
  font-size: 10px;
  font-weight: var(--font-bold);
  color: var(--color-primary-400);
  letter-spacing: 1px;
}
```

---

### Constellation Components

```css
/* Constellation container */
.constellation {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  max-width: 400px;
  margin: 0 auto;
}

/* Constellation canvas (Framer Motion) */
.constellation-canvas {
  width: 100%;
  height: 100%;
  position: relative;
}

/* Star node */
.constellation-star {
  position: absolute;
  width: 32px;
  height: 32px;
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--duration-slow) var(--ease-out);
  z-index: 2;
}

.constellation-star.free {
  background: var(--color-available);
  box-shadow: 0 0 8px var(--glow-available), 0 0 20px var(--glow-available);
  animation: pulseGlow 2s ease-in-out infinite;
}

.constellation-star.busy {
  background: var(--color-space-400);
  opacity: 0.6;
}

.constellation-star.away {
  background: var(--color-away);
  opacity: 0.8;
}

.constellation-star.offline {
  background: var(--color-offline);
  opacity: 0.3;
}

/* Star size variants */
.constellation-star-sm {
  width: 24px;
  height: 24px;
}
.constellation-star-lg {
  width: 40px;
  height: 40px;
}

/* Star label (name) */
.constellation-star-label {
  position: absolute;
  top: calc(100% + 6px);
  left: 50%;
  transform: translateX(-50%);
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
  color: var(--color-text-secondary);
  white-space: nowrap;
  transition: color var(--duration-fast) var(--ease-out);
  pointer-events: none;
}

.constellation-star.free .constellation-star-label {
  color: var(--color-text-primary);
}

/* Inner star icon (tiny star shape or initial) */
.constellation-star-inner {
  font-size: 12px;
  font-weight: var(--font-bold);
  color: white;
}

/* Connection line SVG */
.constellation-line {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.constellation-line-path {
  stroke: var(--glow-connect);
  stroke-width: 1.5;
  fill: none;
  stroke-linecap: round;
  filter: drop-shadow(0 0 4px var(--glow-connect));
}

.constellation-line-path.dim {
  stroke: rgba(56, 189, 248, 0.15);
  stroke-width: 1;
  filter: none;
}

/* Constellation empty state */
.constellation-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-muted);
  gap: var(--spacing-3);
}

.constellation-empty-stars {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  opacity: 0.2;
}
```

---

## Constellation Component — Complete Specification

### Purpose

A reusable animated canvas component that visualizes group members as stars. Connections form when members are free. The entire constellation animates when the group is fully available.

### Input Properties

```typescript
interface ConstellationProps {
  members: ConstellationMember[];
  size?: 'sm' | 'md' | 'lg';
  interactive?: boolean;
  onMemberClick?: (memberId: string) => void;
  className?: string;
}

interface ConstellationMember {
  id: string;
  name: string;
  status: 'free' | 'busy' | 'away' | 'offline';
}
```

### States

#### State 1: 0 users free — "Dark Sky"

```
Visual:
  ⚫     ⚫
  
    ⚫
  
  ⚫     ⚫

- All stars rendered in space-400 at opacity 0.4
- No glow
- No connection lines
- Label text in text-muted

Description: "No one is free right now"
```

#### State 2: 1 user free — "Lone Star"

```
Visual:
  ⚫     ⚫
  
    ⭐️ (glowing)
  
  ⚫     ⚫

- One star: available color + pulseGlow animation + glow-available shadow
- Remaining stars: space-400 at opacity 0.4
- No connection lines
- Free star's label: text-primary (bold)
- Other labels: text-muted

Animation: Free star plays pulseGlow 2s infinite

Description: "Alice is free"
```

#### State 3: 2 users free — "Connected"

```
Visual:
  ⭐️────⭐️
  
    ⚫
  
  ⚫     ⚫

- Two stars: available color + pulseGlow
- Connection line drawn between them
  - Animation: drawLine 800ms ease-smooth on mount
  - Stroke: glow-connect
  - Filter: drop-shadow glow
- Other stars: dim

Animation:
  - Both free stars pulseGlow (desynced by 0.5s)
  - Connection line draws when both become free
  - Line gently fades in/out if status changes

Description: "Alice and Bob are free"
```

#### State 4: Partial group free — "Growing Constellation"

```
Visual:
  ⭐️────⭐️
  
    ⭐️
  
  ⚫     ⚫

- 3+ free stars
- Multiple connection lines forming a partial constellation
- Free stars: connected with lines forming a polygon
- Busy stars: dim, no connections to them

Connection rules:
  - Every pair of free users within 2 positions gets a line
  - If members > 4, only connect adjacent free members in the layout
  - Lines animate sequentially (50ms stagger)

Animation:
  - Stars pulse, lines draw sequentially
  - Partial glow on the constellation

Description: "3 of 5 are free"
```

#### State 5: Entire group free — "Full Constellation"

```
Visual:
  ⭐️────⭐️
  │      │
  ⭐️────⭐️

- All stars: available color + pulseGlow
- Every possible connection drawn
- Constellation container pulse animation
- Strong collective glow

Animation:
  - constellationPulse 3s ease-in-out infinite on entire SVG group
  - drop-shadow: 0 0 30px glow-connect-full
  - Stars desynced pulseGlow
  - Background radial glow appears (bg-nebula)

Transition from previous state:
  1. Remaining stars transition from dim to full glow (300ms)
  2. New connection lines draw (800ms each, 100ms stagger)
  3. Constellation pulse begins (300ms delay after last line)

Description: "Everyone is free!"
```

### Interactions

| Interaction | Trigger | Response | Duration | Easing |
|-------------|---------|----------|----------|--------|
| Hover star | Mouse enter | Scale(1.3), label appears if hidden, tooltip with "Free until X:XX" | 150ms | ease-out |
| Click star | Mouse click | `onMemberClick(member.id)` — navigates to friend comparison | 100ms | ease-out |
| Hover free star pair | Both hovered | Connection line brightens (opacity 1.0, wider stroke 2.5px) | 200ms | ease-out |
| Status change → free | Real-time update | Star fades from dim to glow (500ms), lines draw to connected free members | 500ms | ease-out |
| Status change → busy | Real-time update | Star fades from glow to dim (500ms), connected lines fade away | 400ms | ease-in |
| Group all free | Last member becomes free | All lines draw sequentially, then constellation pulse begins | 1200ms total | ease-smooth |
| Drag star | Pointer down + move | Star follows pointer, other stars and lines remain | — | — |
| Constellation load | Component mount | Stars fade in with stagger (80ms each), lines draw after all stars visible | 1000ms total | ease-out |

### Layout Algorithm

For N members, stars are positioned in a circular or elliptical pattern:

```
N ≤ 3: Equilateral triangle
N = 4: Square
N = 5: Pentagon
N = 6: Hexagon
N = 7: Hexagon + center
N = 8: Two rows of 4
N > 8: Elliptical orbit (2 concentric rings)
```

Positions are deterministic (seeded by member IDs) so the layout is consistent across page loads.

### Implementation Notes

- SVG for connection lines (stroke-dasharray animation for drawing effect)
- CSS/absolute positioning for star nodes
- Framer Motion for enter/exit animations and layout transitions
- requestAnimationFrame for continuous glow pulse (GPU-accelerated)
- ResizeObserver to recalculate positions on container resize
- Stars with `status: 'offline'` should not be interactive
- Connection lines should use `mix-blend-mode: screen` for luminous effect

### Accessibility

- Each star has `role="button"` and `aria-label="Member name — currently free/busy"`
- Constellation has `role="img"` and `aria-label="Constellation of group name — X of Y members free"`
- Status changes announced via `aria-live="polite"` region
- Keyboard navigation: Tab between stars, Enter/Space to select
- Reduced motion: Respect `prefers-reduced-motion` — disable pulse animations, keep opacity transitions only

---

## Tailwind CSS Configuration Reference

```javascript
// tailwind.config.ts — Complete theme extension
import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: 'class',
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        space: {
          900: '#0B1020',
          800: '#0E1526',
          700: '#141B34',
          600: '#1A2340',
          500: '#22305C',
          400: '#2D3D6B',
          300: '#3B4F82',
        },
        primary: {
          50:  '#F5F3FF',
          100: '#EDE9FE',
          200: '#DDD6FE',
          300: '#C4B5FD',
          400: '#A78BFA',
          500: '#8B5CF6',
          600: '#7C3AED',
          700: '#6D28D9',
          800: '#5B21B6',
          900: '#4C1D95',
        },
        accent: {
          50:  '#F0F9FF',
          100: '#E0F2FE',
          200: '#BAE6FD',
          300: '#7DD3FC',
          400: '#38BDF8',
          500: '#0EA5E9',
          600: '#0284C7',
          700: '#0369A1',
        },
        status: {
          available: '#22C55E',
          busy:      '#EF4444',
          away:      '#F59E0B',
          offline:   '#475569',
        },
        text: {
          primary:   '#F8FAFC',
          secondary: '#CBD5E1',
          muted:     '#64748B',
          inverse:   '#0B1020',
        },
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        mono: ['JetBrains Mono', 'SF Mono', 'Fira Code', 'monospace'],
      },
      fontSize: {
        '2xs': '0.625rem',
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      boxShadow: {
        'glow-sm':   '0 0 8px rgba(139, 92, 246, 0.6)',
        'glow-md':   '0 0 16px rgba(139, 92, 246, 0.6)',
        'glow-lg':   '0 0 32px rgba(139, 92, 246, 0.6)',
        'glow-available': '0 0 12px rgba(34, 197, 94, 0.5)',
        'glow-connect':   '0 0 20px rgba(56, 189, 248, 0.5)',
      },
      backdropBlur: {
        xs: '2px',
      },
      animation: {
        'pulse-glow':    'pulseGlow 2s ease-in-out infinite',
        'constellation-pulse': 'constellationPulse 3s ease-in-out infinite',
        'shimmer':       'shimmer 1.5s ease-in-out infinite',
        'fade-in':       'fadeIn 0.2s ease-out',
        'slide-up':      'slideUp 0.3s ease-out',
        'scale-in':      'scaleIn 0.2s cubic-bezier(0.34, 1.56, 0.64, 1)',
        'draw-line':     'drawLine 0.8s ease-smooth forwards',
        'twinkle':       'twinkle 3s ease-in-out infinite',
        'breathe':       'breathe 4s ease-in-out infinite',
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 8px rgba(34, 197, 94, 0.5)' },
          '50%':      { boxShadow: '0 0 20px rgba(34, 197, 94, 0.5), 0 0 40px rgba(34, 197, 94, 0.3)' },
        },
        constellationPulse: {
          '0%, 100%': { opacity: '1', filter: 'brightness(1)' },
          '50%':      { opacity: '0.85', filter: 'brightness(1.15)' },
        },
        shimmer: {
          '0%':   { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        fadeIn: {
          from: { opacity: '0' },
          to:   { opacity: '1' },
        },
        slideUp: {
          from: { opacity: '0', transform: 'translateY(8px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          from: { opacity: '0', transform: 'scale(0.95)' },
          to:   { opacity: '1', transform: 'scale(1)' },
        },
        drawLine: {
          from: { strokeDashoffset: '1000' },
          to:   { strokeDashoffset: '0' },
        },
        twinkle: {
          '0%, 100%': { opacity: '0.6', transform: 'scale(0.9)' },
          '50%':      { opacity: '1', transform: 'scale(1.1)' },
        },
        breathe: {
          '0%, 100%': { opacity: '0.03' },
          '50%':      { opacity: '0.06' },
        },
      },
      transitionTimingFunction: {
        'out-expo':      'cubic-bezier(0.16, 1, 0.3, 1)',
        'in-expo':       'cubic-bezier(0.4, 0, 0.68, 0.06)',
        'spring':        'cubic-bezier(0.34, 1.56, 0.64, 1)',
        'smooth':        'cubic-bezier(0.4, 0, 0.2, 1)',
      },
    },
  },
  plugins: [],
}

export default config
```

---

## globals.css

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --glass-white:  rgba(255, 255, 255, 0.04);
    --glass-border: rgba(255, 255, 255, 0.08);
    --glass-hover:  rgba(255, 255, 255, 0.08);
    --glass-active: rgba(255, 255, 255, 0.12);
  }

  * {
    @apply border-space-500;
  }

  body {
    @apply bg-space-900 text-text-primary font-sans antialiased;
    background:
      radial-gradient(ellipse at 20% 50%, rgba(139, 92, 246, 0.06) 0%, transparent 60%),
      radial-gradient(ellipse at 80% 20%, rgba(56, 189, 248, 0.04) 0%, transparent 50%),
      #0B1020;
    background-attachment: fixed;
  }

  ::selection {
    background: rgba(139, 92, 246, 0.3);
    color: #fff;
  }

  /* Scrollbar styling */
  ::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }
  ::-webkit-scrollbar-track {
    background: transparent;
  }
  ::-webkit-scrollbar-thumb {
    background: var(--color-space-500);
    border-radius: 3px;
  }
  ::-webkit-scrollbar-thumb:hover {
    background: var(--color-space-400);
  }
}

@layer components {
  .glass {
    background: var(--glass-white);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
  }

  .glass-strong {
    background: rgba(20, 27, 52, 0.8);
    backdrop-filter: blur(32px);
    -webkit-backdrop-filter: blur(32px);
    border: 1px solid var(--glass-border);
  }

  .bg-cosmic {
    background:
      radial-gradient(ellipse at 20% 50%, rgba(139, 92, 246, 0.06) 0%, transparent 60%),
      radial-gradient(ellipse at 80% 20%, rgba(56, 189, 248, 0.04) 0%, transparent 50%),
      var(--color-space-900);
  }

  .text-gradient {
    background: linear-gradient(135deg, var(--color-primary-400), var(--color-accent-400));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
}
```
