# Inchworm for Rhino 8

A standalone, cross-platform scale conversion utility for Rhinoceros 3D. Built with Eto.Forms, Inchworm is designed to eliminate the friction of manual scale math during digital fabrication and computational modelling workflows.

## Features

* **Bidirectional Calculation:** Modify the Real-World or Model lengths, and the counterpart updates instantly with zero latency.
* **Session History:** Automatically logs up to 8 recent calculations in a persistent list, providing quick reference during complex physical assemblies.
* **Scale Presets:** One-click standard architectural and engineering ratios (1:50, 1:100, 1:200, 1:500, 1:1000).
* **Frictionless Extraction:** Pressing `Enter` or clicking 'Copy & Log' bakes the formatted result to your clipboard and the Rhino command history.
* **Visual Error Handling:** Invalid inputs trigger a non-blocking UI alert rather than failing silently.
* **Native Cross-Platform:** Compiled for Rhino 8, working seamlessly on both Windows and macOS.

## Installation

### Method 1: Rhino Package Manager (Recommended)
1. Open Rhino 8.
2. Type `PackageManager` in the command line.
3. Search for **Inchworm** and click Install.
4. Restart Rhino and type `Inchworm` to launch the utility.

### Method 2: Manual Installation
1. Go to the [Releases](../../releases) page.
2. Download the latest `.rhp` file.
3. Drag and drop the `.rhp` file into your Rhino 8 viewport.

## License
Distributed under the MIT License.