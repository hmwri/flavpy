import os
from io import BytesIO

import numpy as np
from TsMovieComposer.analyzer.components import SampleTableComponent
from TsMovieComposer.parser import Parser
from TsMovieComposer.analyzer import analyze, FlavMP4
from TsMovieComposer.analyzer.components import TrackComponent
from TsMovieComposer.analyzer.media_data import StreamingSampleData, ChunkData, SampleData, MediaData
from TsMovieComposer.codec import supported_codecs, get_encoder, supported_codec_type
from TsMovieComposer.composer.utils import EmptyMp4Creator, TrackBoxCreator, SampleTableCreator
from TsMovieComposer.composer import Composer
from typing import Literal, BinaryIO, Final


class FlavWriter:
    def __init__(self, path, modal: Literal["taste", "scent"], codec: supported_codec_type, fps: float,
                 add_modal_on:str|None=None):
        self.path = path
        if codec not in supported_codecs:
            raise Exception(f"codec : {codec} is not supported")
        self.codec: supported_codec_type = codec
        self.fps = fps
        self.media_time_scale: int = int(fps * 1000)

        component_subtype: Literal['tast', 'scnt']
        if modal == "taste":
            self.component_subtype : Literal["tast", "scnt"] = "tast"
        elif modal == "scent":
            self.component_subtype: Literal["tast", "scnt"] = "scnt"
        else:
            raise Exception(f"modal:{modal} is not supported.")

        if add_modal_on is not None:
            self.parsed = Parser(add_modal_on).parse()
        else:
            self.parsed = EmptyMp4Creator.create(
                "mp41",
                ["isom", "mp41", "mp42"],
                self.media_time_scale,
                0
            )



        self.flavMp4 = analyze(self.parsed)
        self.data : list[np.ndarray] = []
        self.__sampler_per_chunk = 50
        self.chunks : list[ChunkData] = [ChunkData(samples=[], media_type=self.component_subtype, begin_time=0)]



    def write(self, data:np.ndarray, frame_delta=1):
        encoder = get_encoder(self.codec)
        sample = SampleData(encoder(data), delta=int(frame_delta/self.fps*self.media_time_scale))
        if len(self.chunks[-1]) >= self.__sampler_per_chunk:
            self.chunks.append(ChunkData(samples=[sample], media_type=self.component_subtype,
                                         begin_time=self.chunks[-1].end_time))
        self.chunks[-1].samples.append(sample)






    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.export()

    def export(self):
        if len(self.chunks[0]) == 0:
            raise Exception("There is no data")
        sample_table = SampleTableCreator(self.chunks, codec=self.codec).make_sample_table()
        mov_time_scale = self.flavMp4.mov_header.time_scale
        track_duration = int(self.chunks[-1].end_time * mov_time_scale / self.media_time_scale)
        if self.flavMp4.mov_header.duration < track_duration:
            self.flavMp4.mov_header.duration = track_duration
        composer = Composer(flav_mp4=self.flavMp4)
        composer.set_new_modal(
            self.component_subtype,
            TrackComponent(
                TrackBoxCreator(
                    track_duration=track_duration,
                    media_time_scale=self.media_time_scale,
                    media_duration=self.chunks[-1].end_time,
                    component_subtype=self.component_subtype,
                    component_name="TTTV3",
                    sample_table=sample_table
                ).create()
            ),
            MediaData(self.component_subtype, self.chunks)
        )
        composer.compose()
        composer.write(self.path)



