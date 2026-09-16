#!/usr/bin/env python3
"""Biox Systems -- QR Code Generator.

A command-line application that turns a URL address into a scannable
QR (Quick Response) code image.

QR codes were invented in 1994 by the Japanese company Denso Wave as a
two-dimensional way to represent information in machine-readable form.
This program uses the third-party `qrcode` library (backed by Pillow) to
encode a URL into that two-dimensional grid and save it as a PNG file.

Usage:
    python qr_generator.py https://www.ucumberlands.edu
    python qr_generator.py https://example.com --output output/site.png
    python qr_generator.py https://example.com --ecc H --box-size 12

Author : Sammy Sheu
Course : Artificial Intelligence -- Assignment 2
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import qrcode
from qrcode.constants import (
    ERROR_CORRECT_H,
    ERROR_CORRECT_L,
    ERROR_CORRECT_M,
    ERROR_CORRECT_Q,
)

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

# Error-correction levels supported by the QR standard. A higher level lets a
# damaged or partially obscured code still be read, but stores less data in the
# same number of modules (the small black/white squares that make up the code).
ERROR_CORRECTION_LEVELS: dict[str, tuple[int, str]] = {
    "L": (ERROR_CORRECT_L, "Low -- about 7% of the code can be recovered"),
    "M": (ERROR_CORRECT_M, "Medium -- about 15% of the code can be recovered"),
    "Q": (ERROR_CORRECT_Q, "Quartile -- about 25% of the code can be recovered"),
    "H": (ERROR_CORRECT_H, "High -- about 30% of the code can be recovered"),
}

# URL schemes we are willing to encode. Restricting the list keeps the program
# from silently producing a QR code for something a scanner cannot open.
ALLOWED_SCHEMES: frozenset[str] = frozenset({"http", "https"})

# Default folder for generated images, relative to this script.
DEFAULT_OUTPUT_DIR: Path = Path(__file__).resolve().parent / "output"

# Exit codes returned to the shell (0 = success, non-zero = failure).
EXIT_SUCCESS: int = 0
EXIT_INVALID_INPUT: int = 1
EXIT_WRITE_ERROR: int = 2


# --------------------------------------------------------------------------- #
# Validation helpers
# --------------------------------------------------------------------------- #

def validate_url(url: str) -> str:
    """Check that `url` is a well-formed http/https address.

    Args:
        url: The raw text typed by the user.

    Returns:
        The cleaned-up URL, safe to encode.

    Raises:
        ValueError: If the address is empty, missing a scheme such as
            ``https://``, missing a domain name, or uses a scheme that a
            phone camera would not be able to open.
    """
    cleaned = url.strip()

    if not cleaned:
        raise ValueError("No URL was provided. Please supply a web address.")

    parsed = urlparse(cleaned)

    # urlparse() never fails on garbage input, so we inspect the pieces it
    # produced instead of relying on an exception.
    if not parsed.scheme:
        raise ValueError(
            f"'{cleaned}' is missing a scheme. "
            f"Try 'https://{cleaned}' instead."
        )

    if parsed.scheme.lower() not in ALLOWED_SCHEMES:
        supported = ", ".join(sorted(ALLOWED_SCHEMES))
        raise ValueError(
            f"Unsupported scheme '{parsed.scheme}'. Supported schemes: {supported}."
        )

    if not parsed.netloc:
        raise ValueError(f"'{cleaned}' does not contain a domain name.")

    return cleaned


def build_output_path(url: str, requested: str | None) -> Path:
    """Decide where the PNG file should be written.

    If the user passed ``--output`` that path wins. Otherwise we build a
    readable, unique name from the domain and the current timestamp, for
    example ``output/qrcode_ucumberlands-edu_20260916-134805.png``.

    Args:
        url: The already-validated URL being encoded.
        requested: The value of ``--output``, or None if the flag was omitted.

    Returns:
        The full path of the file to create.
    """
    if requested:
        return Path(requested).expanduser().resolve()

    # Turn "www.ucumberlands.edu" into "ucumberlands-edu" so the file name
    # stays readable and free of characters the file system dislikes.
    domain = urlparse(url).netloc.removeprefix("www.")
    safe_domain = "".join(char if char.isalnum() else "-" for char in domain)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    return DEFAULT_OUTPUT_DIR / f"qrcode_{safe_domain}_{timestamp}.png"


# --------------------------------------------------------------------------- #
# Core logic
# --------------------------------------------------------------------------- #

def generate_qr_code(
    url: str,
    destination: Path,
    ecc: str = "M",
    box_size: int = 10,
    border: int = 4,
    fill_color: str = "black",
    back_color: str = "white",
) -> tuple[Path, int]:
    """Encode `url` as a QR code and save it to `destination`.

    Args:
        url: The validated web address to encode.
        destination: Full path of the PNG file to write.
        ecc: Error-correction level -- one of "L", "M", "Q", or "H".
        box_size: Pixel width of a single module (square) in the code.
        border: Width of the quiet zone, in modules. The QR standard
            requires at least 4 so scanners can find the code's edges.
        fill_color: Color of the dark modules.
        back_color: Color of the background.

    Returns:
        A tuple of (path written, QR version number). The version number
        (1-40) reports how large the symbol had to be to fit the data.

    Raises:
        ValueError: If `ecc` is not a recognised level.
        OSError: If the file could not be written to disk.
    """
    if ecc not in ERROR_CORRECTION_LEVELS:
        valid = ", ".join(ERROR_CORRECTION_LEVELS)
        raise ValueError(f"Unknown error-correction level '{ecc}'. Use one of: {valid}.")

    # version=None lets the library pick the smallest symbol size that can
    # hold the data, which keeps the image compact and easy to scan.
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECTION_LEVELS[ecc][0],
        box_size=box_size,
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=True)

    image = qr.make_image(fill_color=fill_color, back_color=back_color)

    # Create the folder if it does not exist yet, then save the PNG.
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination)

    return destination, qr.version


# --------------------------------------------------------------------------- #
# Command-line interface
# --------------------------------------------------------------------------- #

def parse_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    """Define and read the command-line options.

    Args:
        argv: Argument list to parse. Defaults to ``sys.argv[1:]``.

    Returns:
        The parsed arguments as a namespace object.
    """
    parser = argparse.ArgumentParser(
        prog="qr_generator.py",
        description="Biox Systems QR Code Generator -- turn a URL into a QR code image.",
        epilog="Example: python qr_generator.py https://www.ucumberlands.edu",
    )

    parser.add_argument(
        "url",
        nargs="?",
        help="The web address to encode (for example https://www.ucumberlands.edu). "
             "If omitted, the program will prompt you for it.",
    )
    parser.add_argument(
        "-o", "--output",
        metavar="PATH",
        help="Where to save the PNG. Defaults to an auto-named file in output/.",
    )
    parser.add_argument(
        "-e", "--ecc",
        choices=sorted(ERROR_CORRECTION_LEVELS),
        default="M",
        help="Error-correction level: L=7%%, M=15%%, Q=25%%, H=30%% recovery "
             "(default: %(default)s).",
    )
    parser.add_argument(
        "-b", "--box-size",
        type=int,
        default=10,
        help="Pixel size of each module in the code (default: %(default)s).",
    )
    parser.add_argument(
        "--border",
        type=int,
        default=4,
        help="Quiet-zone width in modules; the standard minimum is 4 "
             "(default: %(default)s).",
    )
    parser.add_argument(
        "--fill-color",
        default="black",
        help="Color of the dark modules (default: %(default)s).",
    )
    parser.add_argument(
        "--back-color",
        default="white",
        help="Background color of the image (default: %(default)s).",
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the application end to end.

    Args:
        argv: Argument list to parse. Defaults to ``sys.argv[1:]``.

    Returns:
        A process exit code: 0 on success, non-zero on failure.
    """
    args = parse_arguments(argv)

    print()
    print("Biox Systems QR Code Generator")
    print("------------------------------")
    # Flush so the banner always appears before any error written to stderr.
    sys.stdout.flush()

    # Accept the URL from the command line, or ask for it interactively so the
    # program is usable even when run with no arguments.
    raw_url = args.url
    if raw_url is None:
        try:
            raw_url = input("Enter a URL to encode: ")
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled by user.", file=sys.stderr)
            return EXIT_INVALID_INPUT

    # Step 1: make sure the input is a usable web address.
    try:
        url = validate_url(raw_url)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return EXIT_INVALID_INPUT

    # Step 2: work out the destination and generate the image.
    destination = build_output_path(url, args.output)

    if args.box_size < 1 or args.border < 0:
        print("Error: --box-size must be 1 or more and --border cannot be negative.",
              file=sys.stderr)
        return EXIT_INVALID_INPUT

    try:
        saved_path, version = generate_qr_code(
            url=url,
            destination=destination,
            ecc=args.ecc,
            box_size=args.box_size,
            border=args.border,
            fill_color=args.fill_color,
            back_color=args.back_color,
        )
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return EXIT_INVALID_INPUT
    except OSError as error:
        print(f"Error: could not save the image -- {error}", file=sys.stderr)
        return EXIT_WRITE_ERROR

    # Step 3: report what was produced. A QR symbol of version N is a grid of
    # (4 * N + 17) modules on each side.
    modules = 4 * version + 17
    print(f"URL      : {url}")
    print(f"Version  : {version}  ({modules}x{modules} modules)")
    print(f"ECC      : {args.ecc} -- {ERROR_CORRECTION_LEVELS[args.ecc][1]}")
    print(f"Saved to : {saved_path}")
    print()
    print("Done. Scan the image with a phone camera to open the URL.")
    print()

    return EXIT_SUCCESS


# Only run the application when this file is executed directly, so the
# functions above can also be imported and reused (or unit tested).
if __name__ == "__main__":
    sys.exit(main())
