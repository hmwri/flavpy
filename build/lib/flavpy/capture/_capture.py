import os
from io import BytesIO

import numpy as np

from flavtool.parser import Parser
from flavtool.analyzer import analyze
from flavtool.analyzer.media_data import StreamingSampleData, ChunkData
from flavtool.codec import supported_codecs, get_decoder ,supported_codec_type
from typing import Literal, BinaryIO, Final

SEEK_FRAME_INDEX : Final[int] = 0
SEEK_MEDIA_TIME : Final[int] = 1
SEEK_REAL_TIME: Final[int] = 2
class ChunkReader :
    def __init__(self, f:BinaryIO, chunk:ChunkData):
        self.chunk = chunk
        self.__chunk_start_pos = chunk[0].start
        f.seek(self.__chunk_start_pos, os.SEEK_SET)

        self.data:BytesIO = BytesIO(f.read(self.chunk.get_size()))
        self.sample_i = 0

    def read_sample(self) -> tuple[bool, bytes|None, StreamingSampleData|None]:
        if self.sample_i >= len(self.chunk) :
            return False, None, None
        sample = self.chunk[self.sample_i]
        data = self.data.read(sample.length)
        self.sample_i += 1
        return True, data, sample

    def seek(self, idx : float|int, seek_mode:int) :
        if seek_mode == SEEK_FRAME_INDEX:
            if not isinstance(idx, int):
                raise TypeError
            if idx >= len(self.chunk) :
                raise Exception("out of chunk size")
            self.sample_i = idx
            sample = self.chunk[self.sample_i]
            self.data.seek(sample.start - self.__chunk_start_pos, os.SEEK_SET)
        elif seek_mode == SEEK_MEDIA_TIME:
            t = idx
            sample_i = 0
            now_t = self.chunk.begin_time
            for sample in self.chunk:
                if now_t <= t < now_t + sample.delta:
                    self.sample_i = sample_i
                    self.data.seek(sample.start - self.__chunk_start_pos, os.SEEK_SET)
                    return
                now_t += sample.delta
                sample_i += 1
            raise Exception(f"frame at {t} not found in this chunk")
        else:
            raise Exception(f"seek_mode{seek_mode} is not supported")



class FlavCapture:
    def __init__(self, path:str, modal:Literal['taste', 'scent']):
        self.__f = open(path, "rb")
        self.parsed = Parser(path, fp=self.__f).parse(read_mdat_bytes=False)
        self.flavMp4 = analyze(self.parsed)
        component_subtype : Literal['tast', 'scnt']
        if modal == "taste":
            component_subtype = "tast"
        elif modal=="scent":
            component_subtype = "scnt"
        else:
            raise Exception(f"modal:{modal} is not supported.")

        track = self.flavMp4.tracks[component_subtype]
        if track is None:
            raise Exception(f"track corresponding {modal} is not found")

        self.media_data = self.flavMp4.media_datas[component_subtype]
        if self.media_data is None:
            raise Exception(f"media data corresponding {modal} is not found")

        self.media_duration = track.media.header.duration

        self.sample_table = self.flavMp4.sample_tables[component_subtype]
        self.time_scale = track.media.header.time_scale

        self.codec = self.sample_table.sample_description.sample_description_table[0].data_format

        if self.codec not in supported_codecs:
            raise Exception(f"codec : {self.codec} is not supported")
        self.codec: supported_codec_type

        self.decoder = get_decoder(self.codec)

        if self.sample_table.time_to_sample.number_of_entries == 1 :
            sample_delta = self.sample_table.time_to_sample.time_to_sample_table[0].sample_delta
            time_scale = track.media.header.time_scale
            self.frame_rate = time_scale / sample_delta
        else :
            self.frame_rate = None

        self.frame_i : int = 0
        self.now_sample: StreamingSampleData | None = None
        self.frame_count = sum([len(c) for c in self.media_data.data])
        self.chunk_i = 0
        self.chunk_reader : ChunkReader |None = ChunkReader(self.__f, self.media_data.data[0])
        self.t = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()

    def read(self, grab=False) -> tuple[bool, np.ndarray|None, int] | None:
        if self.chunk_reader is None:
            if grab:
                return
            return False, None, 0
        ok, data, sample = self.chunk_reader.read_sample()
        if not ok:
            self.chunk_i += 1
            if self.chunk_i >= len(self.media_data.data) :
                if grab:
                    return
                return False, None, 0
            self.chunk_reader = ChunkReader(self.__f, self.media_data.data[self.chunk_i])
            ok, data, sample = self.chunk_reader.read_sample()
        delta = sample.delta
        self.frame_i += 1
        self.t += delta
        if grab:
            return
        return True, self.decoder(data), delta

    def seek(self, pos:int | float, seek_mode:int):
        if seek_mode == SEEK_FRAME_INDEX:
            if not isinstance(pos, int):
                raise TypeError
            n_samples = 0
            for i, chunk in enumerate(self.media_data.data):
                if n_samples <= pos < n_samples + len(chunk):
                    self.chunk_reader = ChunkReader(self.__f, chunk)
                    self.chunk_reader.seek(pos - n_samples, seek_mode=SEEK_FRAME_INDEX)
                    self.chunk_i = i
                    return
                n_samples += len(chunk)
            self.chunk_reader = None
        elif seek_mode == SEEK_MEDIA_TIME or seek_mode == SEEK_REAL_TIME:
            t = pos if seek_mode == SEEK_MEDIA_TIME else int(pos * self.time_scale)
            for i, chunk in enumerate(self.media_data.data):
                if chunk.begin_time <= t < chunk.end_time:
                    self.chunk_reader = ChunkReader(self.__f, chunk)
                    self.chunk_reader.seek(t, seek_mode=SEEK_MEDIA_TIME)
                    self.chunk_i = i
                    return
            self.chunk_reader = None

    def release(self):
        self.__f.close()
















