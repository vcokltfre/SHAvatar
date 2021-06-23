from hashlib import sha512
from re import compile
from typing import List

from PIL import Image, ImageDraw


HASH = compile(r"^[a-f0-9]{128}$")


class Chunkable:
    def __init__(self, bts: bytes) -> None:
        self.bts = bytearray(bts)
        self.idx = 0

    def chunk(self, qty: int) -> List[int]:
        self.idx += qty
        return [self.bts[self.idx+i] for i in range(qty)]


def _generate(hash: Chunkable, size: int) -> Image.Image:
    if size % 8:
        raise ValueError("Size must be divisible by 8.")

    uo, ur = hash.chunk(2)
    use_offset, use_rotation = uo >= 128, ur >= 128

    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw: ImageDraw.ImageDraw = ImageDraw.Draw(image)

    step = size // 16

    for i in range(8):
        start, end = step * i, size - (step * (i / (1.5 if use_offset else 1)))
        draw.ellipse([(start, start), (end, end)], (*hash.chunk(3),255))

    if use_rotation:
        image = image.rotate(sum(hash.chunk(2)))

    return image

def generate(source: str, size: int = 256) -> Image.Image:
    """Generate an avatar with the given options from a string.

    Args:
        source (str): The source string to generate from.
        size (int, optional): The size of the output image. Defaults to 256.

    Raises:
        ValueError: The size specificed was not divisible by 8.

    Returns:
        Image.Image: The generated image.
    """

    hash = Chunkable(sha512(source.encode()).digest())

    return _generate(hash, size)

def generate_from_hash(hash: str, size: int = 256) -> Image.Image:
    """Generate an avatar with the given options from a 512 bit hash.

    Args:
        hash (str): The source hash to generate from.
        size (int, optional): The size of the output image. Defaults to 256.

    Raises:
        ValueError: The hash provided was not a valid 512 bit hex digest.
        ValueError: The size specificed was not divisible by 8.

    Returns:
        Image.Image: The generated image.
    """

    if not HASH.match(hash):
        raise ValueError("Value provided was not a valid hex digest of a 512 bit hash.")

    hash = Chunkable(bytes.fromhex(hash))

    return _generate(hash, size)
