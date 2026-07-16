# Brainslopper ðŸ§ ðŸŽ¨

An AI-generated [Brainloller](https://esolangs.org/wiki/Brainloller) encoder, decoder, and interpreter in a single Python file.

Brainloller is [Brainfuck](https://esolangs.org/wiki/Brainfuck), but the program is stored as pixels in an image. An instruction pointer walks across the image reading colors as commands, and two special colors rotate the pointer's direction so programs can snake across multiple rows.

## Features

- **Run** Brainloller images directly
- **Decode** an image back into plain Brainfuck source
- **Encode** any Brainfuck program into a Brainloller PNG (with automatic wrapping and optional pixel scaling)
- Supports scaled images (e.g. each "cell" is an 8Ã—8 block of pixels) for images that are actually visible to humans

## Requirements

- Python 3.8+
- [Pillow](https://pypi.org/project/pillow/)

```bash
pip install pillow
```

## Usage

### Run an image

```bash
python brainslopper.py run program.png
```

If the image is scaled up (each logical pixel is an NÃ—N block):

```bash
python brainslopper.py run program.png --scale 8
```

### Decode an image to Brainfuck

```bash
python brainslopper.py decode program.png
# ++++++++[>++++[>++>+++>+++>+<<<<-]...
```

### Encode Brainfuck into an image

```bash
python brainslopper.py encode hello.bf hello.png
```

Options:

| Flag | Description |
|------|-------------|
| `-w, --width` | Image width in cells (default: roughly square) |
| `-s, --scale` | Scale factor â€” each cell becomes an NÃ—N pixel block |

Example: encode at width 12, scaled 16Ã— so you can actually see it:

```bash
python brainslopper.py encode hello.bf hello.png -w 12 -s 16
```

## Color reference

| Color | RGB | Command |
|-------|-----|---------|
| Red | (255, 0, 0) | `>` |
| Dark red | (128, 0, 0) | `<` |
| Green | (0, 255, 0) | `+` |
| Dark green | (0, 128, 0) | `-` |
| Blue | (0, 0, 255) | `.` |
| Dark blue | (0, 0, 128) | `,` |
| Yellow | (255, 255, 0) | `[` |
| Dark yellow | (128, 128, 0) | `]` |
| Cyan | (0, 255, 255) | Rotate IP clockwise |
| Dark cyan | (0, 128, 128) | Rotate IP counterclockwise |
| Anything else | â€” | No-op |

Execution starts at the top-left pixel moving right, and halts when the instruction pointer walks off the edge of the image.

## How encoding works

The encoder lays commands out left-to-right, and when it hits the right edge it places two clockwise-rotation pixels to U-turn down and back leftward (and two counterclockwise pixels at the left edge), snaking the program down the image like a boustrophedon. Comments and any non-command characters in the source are stripped automatically.

## Disclaimer

This project is AI-generated slop, hence the name. It appears to work, but no warranties â€” esoteric or otherwise.

## License

MIT
