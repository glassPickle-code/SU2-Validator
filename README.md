# Felpudo SU2 Help Tools

> Created by **glassPickle**  
> Copyright © 2026 glassPickle. All rights reserved.

---

## Overview

**Felpudo SU2 Help Tools** is a lightweight, interactive utility designed to validate, inspect, and clean **SU2 mesh files** for computational fluid dynamics (CFD) workflows. 

It features an interactive ASCII file explorer, automatic workspace scanning for `.su2` files, rigorous marker and element type validation, and automatic generation of clean, Unix-compatible (LF-only) copies.

---

## Features

- **Interactive File Selection:** Automatically detects `.su2` files in your workspace or launches a built-in terminal-based ASCII file explorer to navigate directories.
- **Meshio Compatibility Check:** Safely tests whether `meshio` can parse the mesh geometry without syntax errors.
- **Marker Block & Element Validation:** Inspects interior element codes and boundary marker blocks (`MARKER_TAG`, `MARKER_ELEMS`) to ensure structural integrity.
- **LF-Only Normalization:** Automatically converts and exports a clean, newline-normalized `.clean.su2` copy ready for solvers like SU2 or visualization tools like Gmsh.
- **Pastel Terminal UI:** Styled with a clean ANSI glass-inspired color palette for an elegant command-line experience.

---

## Requirements

- Python 3.x
- `meshio` library

You can install `meshio` via pip if you haven't already:
```bash
pip install meshio
