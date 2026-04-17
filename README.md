# flavpy

## 日本語

`flavpy` は、味覚情報を埋め込める MP4 ベースの形式 FlavMP4 を読み書きするための Python ライブラリです。映像に対応する味データを読み出したり、既存の MP4 に味覚トラックを追加したりする用途を想定しています。

TasteColorizer では、既存映像に含まれる飲食物を GPT-4 Vision などで推定し、その推定結果を味データとして映像に付与することで「味わえる映像」を作ることを目指しています。このリポジトリは、その FlavMP4 の読み書き部分を担います。

参考: https://www.honma.site/ja/works/TasteColorizer/

### インストール

```bash
pip install flavpy
```

ローカルで開発する場合:

```bash
pip install -e .
```

### 味データを読み込む

```python
import flavpy

with flavpy.FlavCapture("taste.mp4", modal="taste") as cap:
    while True:
        ret, data, delta = cap.read()
        if not ret:
            break
        print(data, delta)
```

- `ret`: 読み込みに成功したかどうか
- `data`: デコードされた味データ
- `delta`: メディア時間基準のサンプル持続時間

### 味データを書き込む

```python
import numpy as np
import flavpy

with flavpy.FlavWriter(
    "output.mp4",
    "taste",
    codec="raw5",
    fps=60,
    add_modal_on="input.mp4",
) as writer:
    for i in range(100):
        taste = np.array(
            [(i * 10) % 256, i % 256, i % 256, i % 256, i % 256],
            dtype=np.uint8,
        )
        writer.write(taste)
```

コンテキストマネージャを使わない場合は、書き込み後に `writer.export()` を呼び出してください。

### 構成

- `flavpy/capture/`: FlavMP4 の読み込み
- `flavpy/writer/`: FlavMP4 の書き込み
- `flavpy/inspector/`: ファイル内容の確認
- `setup.py`: パッケージ設定
- `test.py`: ローカルの使用例

### 関連リポジトリ

低レベルな MP4 の解析、味データの codec、MP4 の再構成には `flavtool` を使います。`flavpy` は、アプリケーションから扱いやすい読み書き API を提供する層です。

## English

`flavpy` is a Python library for reading and writing FlavMP4 files, an MP4-based format that can store taste data alongside video.

In the TasteColorizer project, taste values estimated from food scenes are attached to existing videos so that viewers can interact with and taste specific parts of the video. This repository provides the FlavMP4 capture/write layer.

Reference: https://www.honma.site/ja/works/TasteColorizer/

### Install

```bash
pip install flavpy
```

For local development:

```bash
pip install -e .
```

### Read Taste Data

```python
import flavpy

with flavpy.FlavCapture("taste.mp4", modal="taste") as cap:
    while True:
        ret, data, delta = cap.read()
        if not ret:
            break
        print(data, delta)
```

### Write Taste Data

```python
import numpy as np
import flavpy

with flavpy.FlavWriter("output.mp4", "taste", codec="raw5", fps=60, add_modal_on="input.mp4") as writer:
    for i in range(100):
        taste = np.array([(i * 10) % 256, i % 256, i % 256, i % 256, i % 256], dtype=np.uint8)
        writer.write(taste)
```

If you do not use the context manager, call `writer.export()` after writing.

### Structure

- `flavpy/capture/`: FlavMP4 capture API
- `flavpy/writer/`: FlavMP4 writer API
- `flavpy/inspector/`: file inspection helpers
- `setup.py`: package metadata
- `test.py`: local usage example
