# Stellr — Design System

## Brand

- **Name:** Stellr
- **Tagline:** Your people. Your time. Aligned.
- **Emotion:** Calm, connected, confident — warm dark tones, soft glows, gentle motion.

## Color Tokens

### Space (background layers)

| Token | Hex | Usage |
|---|---|---|
| space-900 | `#0B1020` | Base page background |
| space-800 | `#0E1526` | Card surface, sidebar |
| space-700 | `#141B34` | Elevated surfaces |
| space-600 | `#1A2340` | Borders, dividers |
| space-500 | `#22305C` | Subtle borders |
| space-400 | `#2D3D6B` | Hover state bg |
| space-300 | `#3B4F82` | Active state bg |

### Primary (violet accent)

| Token | Hex | Usage |
|---|---|---|
| primary-400 | `#A78BFA` | Icons, decorative glows |
| primary-500 | `#8B5CF6` | Buttons, links, active indicators |
| primary-600 | `#7C3AED` | Button hover, pressed states |

### Accent (sky blue)

| Token | Hex | Usage |
|---|---|---|
| accent-400 | `#38BDF8` | Secondary icons, accent glows |

### Status

| Token | Hex | Usage |
|---|---|---|
| status-available | `#22C55E` | Free, online, green dot |
| status-busy | `#EF4444` | In class, busy, red dot |
| status-away | `#F59E0B` | Away, amber dot |

### Text

| Token | Hex | Usage |
|---|---|---|
| text-primary | `#F8FAFC` | Headings, body copy |
| text-secondary | `#CBD5E1` | Subdued text |
| text-muted | `#64748B` | Labels, metadata |

## Avatar Star Colors

Deterministic palette derived from user UUID (SHA-256 first byte mod length).

| Index | Hex | Name |
|---|---|---|
| 0 | `#A78BFA` | Soft Violet |
| 1 | `#38BDF8` | Sky Blue |
| 2 | `#34D399` | Mint Green |
| 3 | `#FB923C` | Warm Orange |
| 4 | `#F472B6` | Rose Pink |
| 5 | `#818CF8` | Periwinkle |
| 6 | `#FBBF24` | Golden |
| 7 | `#67E8F9` | Cyan |

## Shadows

| Token | Value | Usage |
|---|---|---|
| glow-sm | `0 0 8px rgba(139, 92, 246, 0.6)` | Button default |
| glow-md | `0 0 16px rgba(139, 92, 246, 0.6)` | Button hover |
| glow-lg | `0 0 32px rgba(139, 92, 246, 0.6)` | Large decorative |
| glow-available | `0 0 12px rgba(34, 197, 94, 0.5)` | Green status |
| glow-connect | `0 0 20px rgba(56, 189, 248, 0.5)` | Connection line |

## Glass

```
.glass {
  background: rgba(255, 255, 255, 0.04);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.glass-strong {
  background: rgba(20, 27, 52, 0.8);
  backdrop-filter: blur(32px);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
```

## Typography

- **Body:** Inter / system sans, `text-text-primary`
- **Labels:** `text-xs text-text-muted`
- **Card titles:** `text-lg font-semibold text-text-primary`
- **Page titles:** `text-2xl font-bold text-text-primary`

## Spacing

- Page padding: `p-4 md:p-6 lg:p-8`
- Card padding: `p-5`
- Gap between sections: `space-y-5 md:space-y-6`
- Chip gap: `gap-3`

## Motion

- Page load: stagger-fade-in via Framer Motion (`initial opacity:0 y:12` → `animate`)
- Stagger delay: `0.15s` per group
- Duration: `0.35s` ease-out
- `prefers-reduced-motion`: all animations disabled
