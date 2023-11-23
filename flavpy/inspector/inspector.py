from typing import Literal

from TsMovieComposer.parser import Parser
from TsMovieComposer.analyzer import analyze

class Inspector:
    def __init__(self, path):
        self.path = path
        self.parsed = Parser(path).parse()
        self.flavmp4 = analyze(self.parsed)


    def get_track(self) -> list[Literal["taste","scent","video","sound"]]:
        result :list[Literal["taste","scent","video","sound"]] = []
        for modal, track in self.flavmp4.tracks.items():
            if track is not None:
                if modal == "tast":
                    result.append("taste")
                elif modal == "scnt":
                    result.append("scent")
                elif modal == "vide":
                    result.append("video")
                elif modal == "soun":
                    result.append("sound")

        return result


