import hashlib
import json
from pathlib import Path
from typing import Optional

import typer
from PIL import Image

from pizza_gen.circular_gen import CircularGen
from pizza_gen.logger import enable_debug_log, get_logger
from pizza_gen.pizza_gen import PizzaGen

logger = get_logger(__name__)

app = typer.Typer()


def save_image_safely(img: Image.Image, path: Path, force: bool = False):
    if path.exists() and not force:
        logger.warning(f"'{path}' already exists. Skipping.")
        return

    img.save(path)
    logger.info(f"Successfully saved the image to '{path}'.")


@app.command()
def circular(
    # API
    server_url: str = typer.Option("http://127.0.0.1:7860", "-s", "--server-url"),
    # New image
    width: int = typer.Option(720, "-W", "--width"),
    seed: int = typer.Option(-1, "--seed"),
    prompt: str = typer.Option("A photo of a coffee cup", "-p", "--prompt"),
    negative_prompt_override: Optional[str] = typer.Option(
        None, "--negative-prompt-override"
    ),
    canny_weight: Optional[float] = typer.Option(None, "--canny-weight"),
    # Output
    force_overwrite: bool = typer.Option(False, "-f", "--force-overwrite"),
    output_path: Path = typer.Option(".", "-o", "--output-path"),
    output_filename_template: str = typer.Option(
        "circular_{INFO_HASH}", "-t", "--output-filename-template"
    ),
    output_image_format: Path = typer.Option("webp", "-F", "--output-image-format"),
    # Others
    debug: bool = typer.Option(
        False, "--debug", is_flag=True, help="Output intermediate images for debugging."
    ),
):
    """Generate something circular"""
    # Parse args
    if debug:
        enable_debug_log()

    logger.debug(f"{output_path=}")

    # Generate
    gen = CircularGen(
        server_url=server_url,
        width=width,
        canny_weight=canny_weight,
        debug=debug,
    )
    img, info = gen.generate(
        prompt=prompt,
        neg_prompt_override=negative_prompt_override,
        seed=seed,
    )

    # Define filename
    info_hash = hashlib.sha1(
        info["infotexts"][0].encode("utf-8"), usedforsecurity=False
    ).hexdigest()
    base_filename = output_filename_template.format(INFO_HASH=info_hash)

    # Save outputs
    image_path = output_path / f"{base_filename}.{output_image_format}"
    save_image_safely(img, image_path, force_overwrite)

    json_path = output_path / f"{base_filename}.info.json"
    if not json_path.exists() or force_overwrite:
        with json_path.open("w", encoding="utf-8") as fp:
            fp.write(json.dumps(info, indent=2, ensure_ascii=False))
            logger.info(f"Successfully saved info.json to '{json_path}'.")


@app.command()
def pizza(
    # API
    server_url: str = typer.Option("http://127.0.0.1:7860", "-s", "--server-url"),
    # Input image
    guide_image: Optional[Path] = typer.Option(None, "-g", "--guide-image"),
    # New image
    width: int = typer.Option(720, "-W", "--width"),
    seed: int = typer.Option(-1, "--seed"),
    num_pieces: int = typer.Option(1, "-n", "--num-pieces"),
    total_num_pieces: int = typer.Option(12, "-N", "--total-num-pieces"),
    prompt_override: Optional[str] = typer.Option(None, "--prompt-override"),
    negative_prompt_override: Optional[str] = typer.Option(
        None, "--negative-prompt-override"
    ),
    seg_weight: Optional[float] = typer.Option(None, "--seg-weight"),
    # Output
    force_overwrite: bool = typer.Option(False, "-f", "--force-overwrite"),
    output_path: Path = typer.Option(".", "-o", "--output-path"),
    output_image_format: Path = typer.Option("webp", "-F", "--output-image-format"),
    # Others
    debug: bool = typer.Option(
        False, "--debug", is_flag=True, help="Output intermediate images for debugging."
    ),
):
    """
    Generate pizza
    """
    # Parse args
    if debug:
        enable_debug_log()

    logger.debug(f"{output_path=}")

    guide_image_ = None
    if guide_image:
        logger.info(f"Loading {guide_image=}")
        guide_image_ = Image.open(guide_image)

    # Generate
    gen = PizzaGen(
        server_url=server_url,
        width=width,
        num_pieces=num_pieces,
        total_num_pieces=total_num_pieces,
        seg_weight=seg_weight,
        debug=debug,
    )
    gen._prepare_seg_image()
    img, info = gen.generate(
        depth_guide=guide_image_,
        prompt_override=prompt_override,
        neg_prompt_override=negative_prompt_override,
        seed=seed,
    )

    # Define filename
    info_json = json.dumps(info, indent=2, ensure_ascii=False)
    info_hash = hashlib.sha1(
        info_json.encode("utf-8"), usedforsecurity=False
    ).hexdigest()
    base_filename = f"pizza_{total_num_pieces}p_{num_pieces}p_{info_hash}"

    # Save outputs
    image_path = output_path / f"{base_filename}.{output_image_format}"
    save_image_safely(img, image_path, force_overwrite)

    json_path = output_path / f"{base_filename}.info.json"
    if not json_path.exists() or force_overwrite:
        with json_path.open("w", encoding="utf-8") as fp:
            fp.write(info_json)
            logger.info(f"Successfully saved info.json to '{json_path}'.")
