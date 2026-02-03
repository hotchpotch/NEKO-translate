# 🐈 NEKO-translate

NEKO-translate は、Mac の Apple Silicon に最適化した MLX フレームワークで翻訳を行う CLI アプリです。  
[mlx-lm](https://github.com/ml-explore/mlx-lm) を使って推論の最適化を行っています。

PDF の見開き翻訳が可能な CLI も同梱しており、論文などの長文を交互に読みたいときに便利です。

![PDF bilingual example](https://github.com/hotchpotch/NEKO-translate/raw/main/assets/pdf_translated_example.jpg)

## できること

- 日英翻訳（入力自動判定）
- モデルによっては多言語翻訳にも対応
- 常駐サーバーで起動コストを削減
- 対話モード（引数なしで起動すると REPL）
- ストリーミング出力（対話モードはデフォルト ON）
- PDF 見開き翻訳（pdf2zh_next + neko-translate）

## インストール

### uv tool（おすすめ）

まず uv を入れてください。  
https://docs.astral.sh/uv/getting-started/installation/

そのあと:

```bash
uv tool install neko-translate
```

これで `neko-translate` と `neko-translate-pdf` コマンドが使えます。

### pip

```bash
pip install neko-translate
```

### 開発用

```bash
uv sync
```

## 使い方

### 1) ワンショット翻訳

```bash
neko-translate --text "こんにちは"
```

言語を明示したい場合:

```bash
neko-translate --text "Hello" --input-lang en --output-lang ja
```

### 2) 対話モード

引数なしで起動すると対話モードになります。

```bash
neko-translate
```

```
>> こんにちは
Hello.
>> exit
```

### 3) ストリーミング出力

```bash
neko-translate --stream --server never --text "こんにちは"
```

ストリーミングはサーバー経由では使えません。`--stream` を付けると自動的に直起動に切り替わります。

### 4) サーバーモード

起動コストが気になる場合はサーバーを起動して使ってください。

```bash
neko-translate server start
neko-translate --text "こんにちは"
neko-translate server stop
```

サーバーは `~/.config/neko-translate/` にソケットとログを作ります。

- socket: `~/.config/neko-translate/neko-translate.sock`
- log: `~/.config/neko-translate/server.log`

任意の場所を使いたい場合:

```bash
neko-translate server start \
  --socket ~/.config/neko-translate/test.sock \
  --log-file ~/.config/neko-translate/test.log
```

状態確認:

```bash
neko-translate server status
```

### 5) PDF 翻訳

pdf2zh_next を使って PDF を丸ごと翻訳します。翻訳は neko-translate サーバー経由です。

```bash
neko-translate-pdf paper.pdf
```

デフォルトは `--input en --output ja` です。自動判定したい場合:

```bash
neko-translate-pdf paper.pdf --input auto
```

和英:

```bash
neko-translate-pdf paper_ja.pdf --input ja --output en
```

出力ファイル/ディレクトリを指定:

```bash
neko-translate-pdf paper.pdf --output-pdf translated.pdf
neko-translate-pdf paper.pdf --output-dir ./out
```

## モデル

デフォルトは以下です。

- `hotchpotch/CAT-Translate-0.8b-mlx-q4`

短いエイリアスも用意しています（例: `hymt`）。

モデルのおすすめとライセンス:

- **PLaMo 2 Translate（おすすめ）**
  - 論文や技術文書の翻訳品質が特に良く、まずこれを試すのがおすすめです。
  - 利用には **PLaMo Community License** への同意が必要です（条件付きで商用利用も可能）。
  - ライセンス: [PLaMo Community License](https://plamo.preferredai.jp/info/plamo-community-license-ja)
- **CAT-Translate**
  - MIT ライセンスのため、商用利用でも制約が少なく扱いやすいです。
- **HY-MT**
  - 利用にはライセンスへの同意が必要です。
  - ライセンス: [HY-MT License](https://github.com/Tencent-Hunyuan/HY-MT/blob/main/License.txt)

このプロジェクト（neko-translate 自体）のソースコードは MIT ですが、**利用する翻訳モデルのライセンスはモデルごとに異なります**。必ず各モデルのライセンスを確認してください。

### 動作確認済みの MLX 翻訳モデル（Hugging Face / ライセンス）

| Model | Hugging Face name | License |
| --- | --- | --- |
| [CAT-Translate](https://huggingface.co/collections/cyberagent/cat-translate) | `hotchpotch/CAT-Translate-0.8b-mlx-q4` | MIT |
| [CAT-Translate](https://huggingface.co/collections/cyberagent/cat-translate) | `hotchpotch/CAT-Translate-0.8b-mlx-q8` | MIT |
| [CAT-Translate](https://huggingface.co/collections/cyberagent/cat-translate) | `hotchpotch/CAT-Translate-1.4b-mlx-q4` | MIT |
| [CAT-Translate](https://huggingface.co/collections/cyberagent/cat-translate) | `hotchpotch/CAT-Translate-1.4b-mlx-q8` | MIT |
| [PLaMo 2 Translate](https://huggingface.co/pfnet/plamo-2-translate) | `mlx-community/plamo-2-translate` | [PLaMo Community License](https://plamo.preferredai.jp/info/plamo-community-license-ja) |
| [HY-MT 1.5](https://github.com/Tencent-Hunyuan/HY-MT) | `mlx-community/HY-MT1.5-1.8B-4bit` / `mlx-community/HY-MT1.5-1.8B-8bit` / `mlx-community/HY-MT1.5-7B-4bit` / `mlx-community/HY-MT1.5-7B-8bit` | [HY-MT License](https://github.com/Tencent-Hunyuan/HY-MT/blob/main/License.txt) |

## オプション

主要なものだけ。

- `--input-lang` / `--output-lang`
- `--max-new-tokens`
- `--temperature` / `--top-p` / `--top-k`
- `--server` : `auto` / `always` / `never`
- `--socket` / `--log-file`
- `--verbose`

## 開発

```bash
uv run tox
```

`tox` は pytest / ruff / ty をまとめて実行します。MLX 統合テストも走ります。

## 注意点

- Apple Silicon (macOS) での使用を想定しています。
- 初回はモデルのダウンロードが走ります。
- `uv run` は毎回同期するので、実行前にインストールログが出ます。気になる場合は `--no-sync` を使ってください。

```bash
uv run --no-sync neko-translate --text "こんにちは"
```

## ライセンス

- ソースコード: MIT

## Author

- Yuichi Tateno (@hotchpotch)
