# Ibis

A lightweight toolset for Rhino 3D that covers the small frictions in every
design-to-fabrication workflow — scale conversion, unit normalization,
fabrication tolerances, and batch export.

> Ibis is the successor to Inchworm,
> rebuilt as a full toolset with a new structure and three additional tools.

---

## Tools

**Scale** — Convert between real-world and model dimensions at any ratio.
Set a ratio (or pick a preset), enter a value, and the other side updates
instantly. Session history keeps your recent conversions a click away.

**Normalize** — Fix unit mismatches in received files. Ibis detects the
current document unit, lets you rescale all or selected objects to a target
unit, and optionally updates the document unit system. Fully undoable.

**Tolerance** — Look up fabrication tolerances by process and material.
Covers laser cut, CNC milling, FDM, SLA/DLP, and sheet metal bending.
Shows nominal, ± tolerance, min/max, kerf compensation, and minimum bend
radius where applicable.

**Export** — Batch-convert a list of dimensions at a given scale and export
the result as a CSV — ready for cut lists, spec sheets, or fabrication
documentation.

---

## Installation

### Via Rhino Package Manager (recommended)
1. Open Rhino
2. Run `PackageManager` in the command line
3. Search for **Ibis**
4. Click Install

### Manual
1. Download the latest release from [Food4Rhino](https://www.food4rhino.com/en/app/ibis)
2. Drag the `.yak` file into an open Rhino viewport
3. Run `Ibis` to open the toolset

---

## Requirements

- Rhino 8
- Windows or macOS

---

## Usage

Run `Ibis` from the Rhino command line. The panel floats above the viewport
and stays accessible while you work — you can select objects in Rhino without
closing it.

---

## Support

Ibis is free and open source. If it saves you time on a project, you can
[buy me a coffee](https://ko-fi.com/ruimoreira) — it helps keep the tool
maintained and new features coming.

---

## License

[MIT](LICENSE) — free to use, modify, and distribute.