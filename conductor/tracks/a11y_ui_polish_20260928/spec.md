# Specification: Accessibility & UI Polish

## Overview
Resolve accessibility (WCAG) violations and UI/CSS technical debt identified during the `tracks-2` review.

## Requirements
1. **WCAG Compliance:** Fix nested interactive controls, add `aria-current="page"`, fix inaccessible radio inputs, prevent premature auto-submitting selects, and ensure Escape key/keyboard support for popouts and resizers.
2. **CSS & Frontend Polish:** Add missing design tokens, replace hardcoded depth indentation with CSS variables, extract reusable icon templates, vendor HTMX to remove CDN reliance, and fix BEM class names.
