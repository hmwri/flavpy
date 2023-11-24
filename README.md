# flavpy

flavpyは、味覚情報を埋め込み可能なファイル形式:FlavMP4のキャプチャ、書き込みを行います

## インストール方法

```shell
pip install flavpy
```
## 使用方法
FlavCaptureで読み込み、FlavWriterで書き込みを行います

### FlavCapture
FlavMP4ファイルを読み込みます

```python
import flavpy

#コンテキストマネージャを使う場合
with flavpy.FlavCapture("taste.mp4", modal="taste") as cap:
    while True:
        # ret 読み込み成功したかどうか
        # data 読み込んだデータ(ndarray)
        # delta フレームの持続時間(メディア時間基準)
        ret, data, delta = cap.read()
        if not ret:
            break
```

### FlavWriter
FlavMP4ファイルを書き込みます

```python
import flavpy
import numpy as np
#コンテキストマネージャを使う場合 (使わない場合は最後にwriter.export()してください)

#ここでは、add_modalでファイルを指定して、動画ファイルに味覚を付与しています。
with flavpy.FlavWriter("output2.mp4","taste",codec="raw5", fps=60, add_modal_on="output.mp4") as writer:
    data = [[(i*10)%256, i%256, i%256, i%256, i%256] for i in range(100)]
    for d in data:
        writer.write(np.array(d,dtype=np.uint8))
```