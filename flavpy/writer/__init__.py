from ._writer import FlavWriter
from flavtool.codec.codec_options import MixCodecOption


def generateMixCodecOption(names:list[str], concentrations:list[int] | int, max_amounts:list[int] | int):
    return MixCodecOption.generate(names, concentrations, max_amounts)
