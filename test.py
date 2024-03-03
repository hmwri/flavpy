import time

import numpy as np

import flavpy
from flavpy import codec_options

# with flavpy.FlavCapture("output2.mp4", modal="taste") as cap:
#
#     print(cap.codec_option)
#
#     while True:
#
#         ret, data, delta = cap.read()
#         print(delta)
#         print(cap.time_scale)
#         print(data)
#         if not ret:
#             break
#
#     start = time.time()
#
#     cap.seek(pos=21.2, seek_mode=flavpy.SEEK_REAL_TIME)
#
#     print(time.time() - start)
#


# with flavpy.FlavWriter("output2.mp4", "taste", codec="rmix", fps=2, add_modal_on="output.mp4") as writer:
#     data = [[np.ones((writer.video_width, writer.video_height, 4))] for t in range(20)]
#     for d in data:
#         print("I")
#         writer.write(np.array(d, dtype=np.uint8), 1)



with flavpy.FlavCapture("../HomeiResolve/exported.mp4", modal="taste") as cap:
    cap.parsed.print(0)
    print(cap.flavMp4.media_datas["tast"].data[0].samples[1].start)
