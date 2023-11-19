import time

import numpy as np

import flavpy

# with flavpy.FlavCapture("output2.mp4", modal="taste") as cap:
#
#     while True:
#
#         ret, data, delta = cap.read()
#         print(data)
#         time.sleep(delta/cap.time_scale)
#         if not ret:
#             break
#     start = time.time()
#
#     cap.seek(pos=21.2, seek_mode=flavpy.SEEK_REAL_TIME)
#
#     print(time.time() - start)


with flavpy.FlavWriter("output2.mp4","taste",codec="raw5", fps=60, add_modal=True, base_mp4="output.mp4") as writer:
    data = [[(i*10)%256, i%256, i%256, i%256, i%256] for i in range(100)]
    for d in data:
        writer.write(np.array(d,dtype=np.uint8), d[0])

