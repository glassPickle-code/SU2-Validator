"""
Felpudo SU2 Help tools
Created by glassPickle
Interactive ASCII file explorer, meshio compatibility checker, 
marker block validator, and clean LF-only copy generator.

Run: python felpudo_su2_tools.py
"""
import sys
import os
from pathlib import Path

# Enable ANSI escape sequences on Windows terminals
if os.name == 'nt':
    os.system('')

# --- Kawaii Pastel & Glass Color Palette ---
PINK = "\033[95m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CORAL = "\033[91m"
PURPLE = "\033[35m"
BOLD = "\033[1m"
RESET = "\033[0m"

VALID_ELEM_TYPES = {3, 5, 9, 10, 12, 13, 14}  # line, tri, quad, tet, hex, prism, pyramid

def ascii_file_explorer(current_dir=None):
    """Interactive text-based file explorer to navigate directories and find .su2 files."""
    if current_dir is None:
        current_dir = Path.cwd()
    else:
        current_dir = Path(current_dir)

    while True:
        current_dir = current_dir.resolve()
        print("\n" + PINK + "=" * 65 + RESET)
        print(f"{BOLD}{PINK}[ FELPUDO FILE EXPLORER ]{RESET} by glassPickle -> {CYAN}{current_dir}{RESET}")
        print(PINK + "=" * 65 + RESET)
        
        try:
            items = sorted(list(current_dir.iterdir()), key=lambda x: (not x.is_dir(), x.name.lower()))
        except PermissionError:
            print(f"{CORAL}[!] Permission denied to access this folder.{RESET}")
            current_dir = current_dir.parent
            continue

        valid_choices = {}
        idx = 1
        
        print(f"  {YELLOW}[0]{RESET} {PURPLE}[..]{RESET} Go up to parent directory")
        
        for item in items:
            if item.is_dir():
                print(f"  {YELLOW}[{idx}]{RESET} {CYAN}[DIR]{RESET}  {item.name}/")
                valid_choices[str(idx)] = item
                idx += 1
        
        for item in items:
            if item.is_file() and item.suffix.lower() == '.su2':
                print(f"  {YELLOW}[{idx}]{RESET} {GREEN}[SU2]{RESET}  {item.name}")
                valid_choices[str(idx)] = item
                idx += 1

        for item in items:
            if item.is_file() and item.suffix.lower() != '.su2':
                print(f"  {YELLOW}[{idx}]{RESET} [FILE] {item.name}")
                valid_choices[str(idx)] = item
                idx += 1

        print(PINK + "-" * 65 + RESET)
        print(f"  {PINK}[c]{RESET} Type custom path manually")
        print(f"  {CORAL}[q]{RESET} Quit")
        print(PINK + "=" * 65 + RESET)
        
        choice = input(f"{BOLD}{CYAN}Choose an option: {RESET}").strip().lower()
        
        if choice == 'q':
            print(f"\n{PINK}Exiting Felpudo Tools. Goodbye!{RESET}")
            sys.exit(0)
        elif choice == 'c':
            path_str = input(f"{PINK}Enter full path to .su2 file: {RESET}").strip().strip('"')
            return Path(path_str)
        elif choice == '0':
            if current_dir.parent != current_dir:
                current_dir = current_dir.parent
        elif choice in valid_choices:
            selected = valid_choices[choice]
            if selected.is_dir():
                current_dir = selected
            elif selected.is_file():
                if selected.suffix.lower() == '.su2':
                    return selected
                else:
                    ans = input(f"{YELLOW}'{selected.name}' is not a .su2 file. Select anyway? (y/n): {RESET}")
                    if ans.lower() == 'y':
                        return selected
        else:
            print(f"{CORAL}[!] Invalid choice. Please try again.{RESET}")

def select_file():
    """Quickly lists local .su2 files or launches the ASCII file explorer."""
    if len(sys.argv) == 2:
        return Path(sys.argv[1].strip('"'))

    su2_files = sorted(list(Path(".").glob("**/*.su2")))

    print("\n" + PINK + "=" * 65 + RESET)
    print(f"{BOLD}{PINK}         FELPUDO SU2 HELP TOOLS{RESET} | by glassPickle")
    print(PINK + "=" * 65 + RESET)

    if su2_files:
        print(f"{CYAN}Quick select from your workspace:{RESET}")
        for idx, file_path in enumerate(su2_files, 1):
            print(f"  {YELLOW}[{idx}]{RESET} {file_path}")
        print(PINK + "-" * 65 + RESET)
    
    print(f"  {PINK}[e]{RESET} Launch ASCII File Explorer (browse other folders)")
    print(f"  {YELLOW}[0]{RESET} Type custom file path manually")
    print(PINK + "=" * 65 + RESET)

    choice = input(f"{BOLD}{CYAN}Enter your choice: {RESET}").strip().lower()
    
    if choice == 'e':
        return ascii_file_explorer()
    elif choice == '0' or not choice.isdigit():
        path_str = input(f"{PINK}Enter path to .su2 file: {RESET}").strip().strip('"')
        return Path(path_str)

    idx = int(choice) - 1
    if 0 <= idx < len(su2_files):
        return su2_files[idx]
    else:
        print(f"{YELLOW}Invalid selection. Launching file explorer instead...{RESET}")
        return ascii_file_explorer()

def main():
    p = select_file()
    
    if not p.exists():
        print(f"\n{CORAL}[ ERROR ] File not found: {p.resolve()}{RESET}")
        sys.exit(1)

    print(f"\n{CYAN}--- Analyzing Mesh: {BOLD}{p.name}{RESET}{CYAN} ---{RESET}\n")
    
    raw = p.read_bytes()
    text = raw.decode("utf-8-sig", errors="replace")

    # ---- Write a cleaned LF-only copy ----
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
    clean_path = p.with_name(p.stem + ".clean.su2")
    clean_path.write_text(cleaned, encoding="ascii", newline="\n")

    # ---- Check with meshio first ----
    meshio_ok = True
    meshio_error = None
    try:
        import meshio
        meshio.read(str(clean_path))
    except Exception as e:
        meshio_ok = False
        meshio_error = str(e)

    lines = text.splitlines()

    ndime = nelem = npoin = nmark = None
    nelem_idx = npoin_idx = nmark_idx = None
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("NDIME="):
            ndime = int(s.split("=")[1])
        elif s.startswith("NELEM=") and nelem is None:
            nelem = int(s.split("=")[1]); nelem_idx = i
        elif s.startswith("NPOIN=") and npoin is None:
            npoin = int(s.split("=")[1]); npoin_idx = i
        elif s.startswith("NMARK="):
            nmark = int(s.split("=")[1]); nmark_idx = i

    # ---- Check interior element types ----
    bad_types = set()
    if nelem_idx is not None:
        for ln in lines[nelem_idx + 1 : nelem_idx + 1 + nelem]:
            parts = ln.split()
            if not parts:
                continue
            try:
                t = int(parts[0])
            except ValueError:
                continue
            if t not in VALID_ELEM_TYPES:
                bad_types.add(t)

    # ---- Walk and validate marker blocks ----
    issues = []
    found_markers = 0
    if nmark_idx is not None:
        cursor = nmark_idx + 1
        while cursor < len(lines) and found_markers < (nmark or 0):
            line = lines[cursor].strip()
            if not line:
                cursor += 1
                continue
            if not line.startswith("MARKER_TAG="):
                issues.append(f"Expected a boundary name marker at line {cursor+1}, but found: {line!r}")
                break

            tag_raw = line.split("=", 1)[1]
            tag = tag_raw.strip()
            cursor += 1

            if cursor >= len(lines) or not lines[cursor].strip().startswith("MARKER_ELEMS="):
                issues.append(f"Missing element count declaration right after boundary tag '{tag}'.")
                break

            try:
                n_elems = int(lines[cursor].strip().split("=")[1])
            except ValueError:
                issues.append(f"Invalid element count format for boundary '{tag}'.")
                break
            cursor += 1

            block = lines[cursor : cursor + n_elems]
            if len(block) != n_elems:
                issues.append(f"Boundary '{tag}' expects {n_elems} elements, but only {len(block)} lines remain.")
                break

            for j, bl in enumerate(block):
                parts = bl.split()
                if not parts:
                    continue
                try:
                    t = int(parts[0])
                except ValueError:
                    continue
                if t not in VALID_ELEM_TYPES:
                    issues.append(f"Boundary '{tag}' has an unexpected element type code ({t}) at row {j+1}.")

            cursor += n_elems
            found_markers += 1
    else:
        issues.append("No NMARK header line found to declare boundaries.")

    # ---- Professional Health Report ----
    print(PINK + "=" * 65 + RESET)
    print(f"{BOLD}{PINK}            FELPUDO MESH HEALTH REPORT{RESET}")
    print(PINK + "=" * 65 + RESET)
    
    if meshio_ok and not bad_types and not issues:
        print(f"Status: {GREEN}[ PERFECT ] - File is fully valid and healthy{RESET}\n")
        print(f" • Meshio Validation  : {GREEN}Passed with zero errors{RESET}")
        print(f" • Spatial Dimensions : {CYAN}{ndime}D{RESET}")
        print(f" • Total Grid Points  : {CYAN}{npoin:,}{RESET}")
        print(f" • Interior Elements  : {CYAN}{nelem:,}{RESET}")
        print(f" • Boundary Markers   : {CYAN}{found_markers} declared{RESET}")
        print(f"\n{GREEN}All checks passed successfully. Ready for simulation.{RESET}")
    else:
        print(f"Status: {CORAL}[ ATTENTION NEEDED ] - Issues were found{RESET}\n")
        if meshio_ok:
            print(f" • Meshio Check       : {GREEN}Passed successfully.{RESET}")
        else:
            print(f" • Meshio Check       : {CORAL}Failed ({meshio_error}){RESET}")
        
        if bad_types:
            print(f" • Element Types      : {CORAL}Found unrecognized code types: {bad_types}{RESET}")
        
        if issues:
            print(f"\n{YELLOW} Specific Problems Detected:{RESET}")
            for issue in issues:
                print(f"   - {CORAL}{issue}{RESET}")
        else:
            print(f" • Marker Structure   : {GREEN}Appears logically consistent.{RESET}")

    print(PINK + "-" * 65 + RESET)
    print(f"{CYAN}A clean, formatted copy was saved locally as:{RESET}")
    print(f" {PURPLE}➔ {clean_path.resolve()}{RESET}")
    print(PINK + "=" * 65 + RESET)

if __name__ == "__main__":
    main()
