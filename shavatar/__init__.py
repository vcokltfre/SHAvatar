from hashlib import sha512
from typing import List

from PIL import Image, ImageDraw


class Chunkable:
    def __init__(self, bts: bytes) -> None:
        self.bts = bytearray(bts)
        self.idx = 0

    def chunk(self, qty: int) -> List[int]:
        self.idx += qty
        return [self.bts[self.idx+i] for i in range(qty)]


def generate(source: str, size: int = 256) -> Image.Image:
    """Generate an avatar with the given options from a string."""

    if size % 8:
        raise ValueError("Size must be divisible by 8.")

    source_hash = Chunkable(sha512(source.encode()).digest())

    uo, ur = source_hash.chunk(2)
    use_offset, use_rotation = uo >= 128, ur >= 128

    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw: ImageDraw.ImageDraw = ImageDraw.Draw(image)

    step = size // 16

    for i in range(8):
        start, end = step * i, size - (step * (i / (1.5 if use_offset else 1)))
        draw.ellipse([(start, start), (end, end)], (*source_hash.chunk(3),255))

    if use_rotation:
        image = image.rotate(sum(source_hash.chunk(2)))

    return image
