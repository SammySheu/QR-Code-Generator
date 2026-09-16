# Biox Systems — QR Code Generator

A Python command-line application that converts a URL address into a scannable
QR (Quick Response) code image.

QR codes were invented in 1994 by the Japanese company **Denso Wave** as a
two-dimensional way of representing information in machine-readable form. This
project encodes a web address into that two-dimensional grid and saves it as a
PNG file that any phone camera can scan.

**Course:** Artificial Intelligence — Assignment 2

---

## Features

- Encodes any `http` / `https` URL into a PNG QR code
- Validates the input and reports clear, specific errors (missing scheme,
  unsupported scheme, missing domain)
- Automatic, collision-free output file names based on the domain and timestamp
- Selectable error-correction level (L / M / Q / H)
- Adjustable module size, quiet-zone border, and colors
- Works with a command-line argument or an interactive prompt
- Meaningful process exit codes for use in scripts (0 = success)

---

## Requirements

- Python 3.9 or newer
- The packages listed in `requirements.txt`:
  - `qrcode` — builds the QR code matrix
  - `pillow` — renders and saves the PNG image

---

## Setup

```bash
# 1. Clone the repository
git clone <your-repository-url>
cd Assignment2

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows

# 3. Install the dependencies from the manifest file
pip install -r requirements.txt
```

---

## Usage

Generate a QR code for a URL:

```bash
python qr_generator.py https://www.ucumberlands.edu
```

Run with no arguments and the program will prompt you:

```bash
python qr_generator.py
```

Choose where to save the file:

```bash
python qr_generator.py https://example.com --output output/example.png
```

Use high error correction and larger modules:

```bash
python qr_generator.py https://example.com --ecc H --box-size 12
```

Show all options:

```bash
python qr_generator.py --help
```

### Command-line options

| Option | Default | Description |
| --- | --- | --- |
| `url` | *(prompted)* | The web address to encode |
| `-o`, `--output` | auto-named in `output/` | Path of the PNG file to write |
| `-e`, `--ecc` | `M` | Error correction: `L` 7%, `M` 15%, `Q` 25%, `H` 30% |
| `-b`, `--box-size` | `10` | Pixel size of each module in the code |
| `--border` | `4` | Quiet-zone width in modules (standard minimum is 4) |
| `--fill-color` | `black` | Color of the dark modules |
| `--back-color` | `white` | Background color |

---

## Example output

```
$ python qr_generator.py https://www.ucumberlands.edu

Biox Systems QR Code Generator
------------------------------
URL      : https://www.ucumberlands.edu
Version  : 3  (29x29 modules)
ECC      : M -- Medium -- about 15% of the code can be recovered
Saved to : output/qrcode_ucumberlands-edu_20260916-135230.png

Done. Scan the image with a phone camera to open the URL.
```

The *version* number (1–40) reports how large the symbol had to be to hold the
data. A version-N symbol is a grid of `4 × N + 17` modules on each side.

---

## Project structure

```
Assignment2/
├── qr_generator.py     Application source code
├── requirements.txt    Manifest file (dependency list)
├── README.md           This file
├── .gitignore          Files excluded from version control
├── docs/               Screenshot and Word deliverable
└── output/             Generated QR code images
```

---

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | QR code generated successfully |
| `1` | Invalid input (bad URL or bad option value) |
| `2` | The image file could not be written to disk |
