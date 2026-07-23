# Availability Engine — Worked Example

## Slot Model

A day is divided into 9 fixed academic slots (SLOT_BOUNDARIES):

| Slot | Start | End   |
|------|-------|-------|
| 0    | 09:00 | 09:50 |
| 1    | 09:50 | 10:40 |
| 2    | 11:00 | 11:50 |
| 3    | 11:50 | 12:40 |
| 4    | 13:30 | 14:20 |
| 5    | 14:20 | 15:10 |
| 6    | 15:20 | 16:10 |
| 7    | 16:10 | 17:00 |
| 8    | 17:00 | 17:50 |

A user's day is a 9-element bit array: `1` = busy (has a class), `0` = free.

---

## Example: Alice + Bob

### Busy slots from timetable

| User   | Busy slot indices |
|--------|------------------|
| Alice  | {0, 1, 4}        |
| Bob    | {0, 3, 4, 7}     |

### Step 1: Build bit arrays

```
Alice: [1, 1, 0, 0, 1, 0, 0, 0, 0]    (busy at 0, 1, 4)
Bob:   [1, 0, 0, 1, 1, 0, 0, 1, 0]    (busy at 0, 3, 4, 7)
```

### Step 2: OR → combined busy

```
OR:    [1, 1, 0, 1, 1, 0, 0, 1, 0]
```

1 if **any** user is busy in that slot.

### Step 3: Invert → shared free

```
FREE:  [0, 0, 1, 0, 0, 1, 1, 0, 1]
```

1 if **all** users are simultaneously free in that slot.

### Step 4: Merge adjacent free bits

Scan the FREE array left to right:
- Slot 2 (11:00–11:50) is free → start a window
- Slot 3 (11:50–12:40) is busy → close window → `11:00–11:50`
- Slot 5 (14:20–15:10) is free → start a window
- Slot 6 (15:20–16:10) is free → still in same window (adjacent via back-to-back timing)
  Wait — slots 5 and 6 are NOT adjacent: slot 5 ends at 15:10, slot 6 starts at 15:20.
  There is a 10-minute gap (15:10–15:20). Should they merge?

**Design decision**: Slots are merged as contiguous in the bit array, regardless of gaps.
Slot 5 ends at 15:10, slot 6 starts at 15:20 — a 10 min gap. But the bit array has
`free_bits[5] = 1` and `free_bits[6] = 1` with no busy bit between them, so they ARE
merged. The resulting window spans from the start of slot 5 to the end of slot 6:
14:20–16:10. This is intentional — the gap is a passing period and treated as
effectively free within the larger block.

```
FREE:  [0, 0, 1, 0, 0, 1, 1, 0, 1]
                      ^--^--^     ^
windows: 11:00–11:50 | 14:20–16:10 | 17:00–17:50
```

### Step 5: Derived values

| Metric | Value |
|--------|-------|
| shared_windows | 11:00–11:50, 14:20–16:10, 17:00–17:50 |
| longest_window | 14:20–16:10 (110 min) |
| current_overlap | depends on `now` — e.g. at 14:30 → true |
| next_slot | depends on `now` — e.g. at 10:00 → 11:00–11:50 |

---

## Verification

Hand-computing the same input:

```
Alice busy: [1,1,0,0,1,0,0,0,0]
Bob busy:   [1,0,0,1,1,0,0,1,0]
OR:         [1,1,0,1,1,0,0,1,0]  (anyone busy)
INVERT:     [0,0,1,0,0,1,1,0,1]  (all free)
```

Merging free runs:
- idx 2: start=11:00, idx 2 ends → end=11:50 → window `11:00–11:50`
- idx 5-6: start=14:20, idx 6 ends → end=16:10 → window `14:20–16:10`
- idx 8: start=17:00, idx 8 ends → end=17:50 → window `17:00–17:50`

✓ Matches algorithm output.

---

## Edge Cases

1. **No shared free time**: FREE array is all zeros → `shared_windows: []`, all derived fields null/false.
2. **All free all day**: FREE array is all ones → one window `09:00–17:50`.
3. **Single slot free**: e.g. FREE = `[0,0,0,0,0,1,0,0,0]` → one window `14:20–15:10`.
4. **Only one user in comparison**: returns empty windows (requires ≥2).
5. **User has no section assigned**: treated as fully free (all zeros in busy array).
