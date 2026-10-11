# CSS Coding Rules

## Rule Structure & Nesting
- **Native Nesting Preference:** Always prefer native CSS nesting using `&` where appropriate (e.g. `&:hover`, `&[data-state]`, `& > *`, `&::before`), rather than repeating multiple classes at the same level or flat compound selectors.
- **Cleanliness:** Avoid overly deep nesting hierarchies; keep selectors scoped and performant.

## Declaration Grouping & Order
Declarations within each CSS rule must be grouped by type and strictly ordered as follows (do not add comments, preserve the order):
1. **Positioning:** `position`, `top`, `right`, `bottom`, `left`, `inset`, `inset-block`, `inset-inline`, `z-index`.
2. **Display & Box Model:** `display`, `flex`, `grid`, `gap`, `align-items`, `justify-content`, `box-sizing`, `width`, `height`, `margin`, `padding`, `border`, `border-radius`, `overflow`, etc.
3. **Colour & Visuals:** `color`, `background`, `background-color`, `box-shadow`, `opacity`, etc.
4. **Typography:** `font`, `font-family`, `font-size`, `font-weight`, `line-height`, `letter-spacing`, `text-align`, `white-space`, etc.
5. **Other / Misc:** `cursor`, `transition`, `animation`, `transform`, `pointer-events`, `appearance`, etc.
