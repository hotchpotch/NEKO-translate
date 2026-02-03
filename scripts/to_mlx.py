#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

DEFAULT_MODELS = [
    "cyberagent/CAT-Translate-1.4b",
    "cyberagent/CAT-Translate-0.8b",
]
DEFAULT_QBITS = [8, 4]
SUPPORTED_QBITS = {4, 8}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert Hugging Face models to MLX format (4-bit/8-bit)."
    )
    parser.add_argument(
        "--model",
        action="append",
        dest="models",
        help="Hugging Face model repo (can be repeated).",
    )
    parser.add_argument(
        "--qbits",
        nargs="+",
        type=int,
        default=DEFAULT_QBITS,
        help="Quantization bits (default: 8 4).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output/mlx"),
        help="Base output directory.",
    )
    parser.add_argument(
        "--q-group-size",
        type=int,
        default=None,
        help="Quantization group size for mlx_lm.convert.",
    )
    parser.add_argument(
        "--dtype",
        choices=["float16", "bfloat16", "float32"],
        default=None,
        help="Data type for non-quantized parameters.",
    )
    parser.add_argument(
        "--trust-remote-code",
        action="store_true",
        help="Trust remote code when loading tokenizer.",
    )
    return parser.parse_args()


def build_command(
    model: str,
    out_dir: Path,
    qbits: int,
    q_group_size: int | None,
    dtype: str | None,
    trust_remote_code: bool,
) -> list[str]:
    cmd = [
        sys.executable,
        "-m",
        "mlx_lm",
        "convert",
        "--hf-path",
        model,
        "--mlx-path",
        str(out_dir),
        "-q",
        "--q-bits",
        str(qbits),
    ]
    if q_group_size is not None:
        cmd.extend(["--q-group-size", str(q_group_size)])
    if dtype is not None:
        cmd.extend(["--dtype", dtype])
    if trust_remote_code:
        cmd.append("--trust-remote-code")
    return cmd


def main() -> int:
    args = parse_args()
    models = args.models or DEFAULT_MODELS
    qbits_list = args.qbits

    invalid_qbits = [q for q in qbits_list if q not in SUPPORTED_QBITS]
    if invalid_qbits:
        raise SystemExit(
            f"Unsupported qbits: {invalid_qbits}. Supported values: {sorted(SUPPORTED_QBITS)}"
        )

    for model in models:
        for qbits in qbits_list:
            out_dir = args.output_dir / model / f"q{qbits}"
            out_dir.parent.mkdir(parents=True, exist_ok=True)
            if out_dir.exists():
                raise SystemExit(
                    f"Output path already exists: {out_dir}. "
                    "Please delete/move it or choose another output directory."
                )
            cmd = build_command(
                model,
                out_dir,
                qbits,
                args.q_group_size,
                args.dtype,
                args.trust_remote_code,
            )
            print("Running:", " ".join(shlex.quote(part) for part in cmd))
            subprocess.run(cmd, check=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
