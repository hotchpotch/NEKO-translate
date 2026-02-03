#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Iterable

PROMPT_TEMPLATE = "Translate the following {src_lang} text into {tgt_lang}.\n\n{src_text}"
DEFAULT_MLX_MODEL = Path("output/mlx/cyberagent/CAT-Translate-0.8b/q4")
LANG_CODE_MAP = {
    "ja": "ja",
    "jp": "ja",
    "japanese": "ja",
    "日本語": "ja",
    "en": "en",
    "eng": "en",
    "english": "en",
}
LANG_NAME_MAP = {
    "ja": "Japanese",
    "en": "English",
}
SUPPORTED_LANGS = {"ja", "en"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Translate with CAT-Translate (MLX only).",
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=DEFAULT_MLX_MODEL,
        help="Path to MLX model directory (default: CAT-Translate-0.8b q4).",
    )
    parser.add_argument(
        "--text",
        help="Input text. If omitted, read from stdin.",
    )
    parser.add_argument(
        "--input-lang",
        help="Input language (en/ja).",
    )
    parser.add_argument(
        "--output-lang",
        help="Output language (en/ja).",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=512,
        help="Maximum number of new tokens to generate.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.0,
        help="Sampling temperature. 0 disables sampling.",
    )
    parser.add_argument(
        "--top-p",
        type=float,
        default=1.0,
        help="Top-p sampling value.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=0,
        help="Top-k sampling value.",
    )
    parser.add_argument(
        "--trust-remote-code",
        action="store_true",
        help="Trust remote code when loading tokenizers.",
    )
    parser.add_argument(
        "--no-chat-template",
        action="store_true",
        help="Disable chat template even if the tokenizer provides one.",
    )
    return parser.parse_args()


def read_text(args: argparse.Namespace) -> str:
    if args.text is not None:
        return args.text
    if sys.stdin.isatty():
        raise SystemExit("Provide --text or pipe input via stdin.")
    data = sys.stdin.read()
    if not data.strip():
        raise SystemExit("No input text provided via stdin.")
    return data


def normalize_lang(value: str | None) -> str | None:
    if value is None:
        return None
    key = value.strip().lower()
    normalized = LANG_CODE_MAP.get(key)
    if normalized is None:
        raise SystemExit(
            f"Unsupported language '{value}'. Supported: {sorted(SUPPORTED_LANGS)}"
        )
    return normalized


def detect_lang(text: str) -> str:
    from fast_langdetect import detect

    results = detect(text, k=3, model="auto")
    if isinstance(results, dict):
        results_iter: Iterable[dict[str, Any]] = [results]
    else:
        results_iter = results

    for item in results_iter:
        lang = item.get("lang")
        if lang in SUPPORTED_LANGS:
            return lang

    raise SystemExit("Could not detect language as English or Japanese.")


def resolve_languages(args: argparse.Namespace, text: str) -> tuple[str, str]:
    input_lang = normalize_lang(args.input_lang)
    output_lang = normalize_lang(args.output_lang)

    if input_lang is None and output_lang is None:
        input_lang = detect_lang(text)
        output_lang = "ja" if input_lang == "en" else "en"
        sys.stderr.write(f"[INFO] Detected {input_lang} -> {output_lang}\n")
        return input_lang, output_lang

    if input_lang is None and output_lang is not None:
        input_lang = "ja" if output_lang == "en" else "en"
        return input_lang, output_lang

    if input_lang is not None and output_lang is None:
        output_lang = "ja" if input_lang == "en" else "en"
        return input_lang, output_lang

    if input_lang not in SUPPORTED_LANGS or output_lang not in SUPPORTED_LANGS:
        raise SystemExit("Only English and Japanese are supported.")

    if input_lang == output_lang:
        raise SystemExit("Input and output languages must be different.")

    return input_lang, output_lang


def run_mlx(prompt: str, args: argparse.Namespace) -> str:
    from mlx_lm import load
    from mlx_lm.generate import generate
    from mlx_lm.sample_utils import make_sampler

    model, tokenizer = load(
        str(args.model),
        tokenizer_config={
            "trust_remote_code": True if args.trust_remote_code else None
        },
    )

    messages = [{"role": "user", "content": prompt}]
    if not args.no_chat_template and hasattr(tokenizer, "apply_chat_template"):
        prompt_text = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=False,
        )
    else:
        prompt_text = prompt

    sampler = None
    if (args.temperature and args.temperature > 0) or (
        args.top_p and args.top_p < 1.0
    ) or (args.top_k and args.top_k > 0):
        sampler = make_sampler(
            temp=args.temperature,
            top_p=args.top_p,
            top_k=args.top_k,
        )

    gen_kwargs: dict[str, Any] = {"max_tokens": args.max_new_tokens}
    if sampler is not None:
        gen_kwargs["sampler"] = sampler

    return generate(model, tokenizer, prompt_text, **gen_kwargs)


def main() -> int:
    args = parse_args()
    text = read_text(args)
    input_lang, output_lang = resolve_languages(args, text)

    prompt = PROMPT_TEMPLATE.format(
        src_lang=LANG_NAME_MAP[input_lang],
        tgt_lang=LANG_NAME_MAP[output_lang],
        src_text=text,
    )

    translation = run_mlx(prompt, args)
    print(translation)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
