import time

import numpy as np

import flavpy
from flavpy import codec_options

with flavpy.FlavCapture("output2.mp4", modal="taste") as cap:

    print(cap.codec_option)

    while True:

        ret, data, delta = cap.read()
        print(delta)
        print(cap.time_scale)
        print(data)
        if not ret:
            break
    start = time.time()

    cap.seek(pos=21.2, seek_mode=flavpy.SEEK_REAL_TIME)

    print(time.time() - start)


with flavpy.FlavWriter("output2.mp4", "taste", codec="rmix", fps=60, add_modal_on="output.mp4",
                       codec_option=codec_options.MixCodecOption(
                           [codec_options.MixInfo("aacc", 1.0, 1.0),
                            codec_options.MixInfo("aacc", 1.0, 1.0),
                            codec_options.MixInfo("aacc", 1.0, 1.0),
                            codec_options.MixInfo("aacc", 1.0, 1.0),
                            codec_options.MixInfo("aacc", 1.0, 1.0)]

                       )) as writer:
    data = [[(i * 10) % 256, i % 256, i % 256, i % 256, i % 256] for i in range(100)]
    for d in data:
        writer.write(np.array(d, dtype=np.uint16), d[0])
