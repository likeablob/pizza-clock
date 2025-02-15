from random import randint
from typing import List, Optional, cast
from urllib.parse import urlparse

import webuiapi
from PIL import Image, ImageDraw

from pizza_gen.logger import console, get_logger

from .ade20k import ADE20K

logger = get_logger(__name__)


class PizzaGen:
    def __init__(
        self,
        server_url: str,
        width: int,
        num_pieces: int,
        total_num_pieces: int = 12,
        seg_weight: Optional[float] = None,
        debug: bool = False,
    ) -> None:
        self.client = self._create_client(server_url)
        self.width = width
        self.num_pieces = num_pieces
        self.total_num_pieces = total_num_pieces
        self.seg_weight = seg_weight
        self.debug = debug

    def _create_client(self, url: str):
        parsed = urlparse(url)

        if parsed.hostname is None:
            raise Exception("Failed to get hostname.")
        if parsed.port is None:
            raise Exception("Failed to get port.")

        return webuiapi.WebUIApi(
            host=parsed.hostname, port=parsed.port, use_https=parsed.scheme == "https"
        )

    def _prepare_seg_image(self):
        image_size = (self.width, self.width)

        im = Image.new("RGBA", image_size, "white")
        draw = ImageDraw.Draw(im)

        pizza_d = image_size[0] * 0.90
        pizza_padding = (image_size[0] - pizza_d) / 2

        # Draw a dish somewhat smaller than the pizza
        dish_padding = pizza_padding + 10
        draw.ellipse(
            (
                (dish_padding, dish_padding),
                (image_size[0] - dish_padding, image_size[1] - dish_padding),
            ),
            # The "DISH" class is not suitable for rendering an empty dish
            fill=ADE20K.ROCK,
            outline="white",
            width=0,
        )

        # Draw pieces of pizza
        for i in range(0, self.num_pieces):
            draw.pieslice(
                (
                    (pizza_padding, pizza_padding),
                    (image_size[0] - pizza_padding, image_size[1] - pizza_padding),
                ),
                start=360 / self.total_num_pieces * i - randint(0, 5),
                end=360 / self.total_num_pieces * (i + 1) + randint(0, 5),
                fill=ADE20K.FOOD,
                outline="white",
                width=0,
            )

        # Rotate 90 deg CCW to shift the origin to 12 o'clock
        im = im.transpose(Image.Transpose.ROTATE_90)

        if self.debug:
            logger.debug("Saving seg_image to debug_seg_image.png")
            im.save("debug_seg_image.png")

        return im

    def _prepare_cn_seg_model(self, models: List[str], weight: float):
        seg_image = self._prepare_seg_image()

        seg_model = next((x for x in models if "sd15_seg" in x), None)
        logger.debug(f"{seg_model=}")

        if seg_model is None:
            raise Exception(
                (
                    "Failed to find a proper segmentation model,"
                    "which contains 'sd15_seg' in its name."
                )
            )

        return webuiapi.ControlNetUnit(
            image=seg_image,  # type: ignore
            module="none",
            model=seg_model,
            weight=weight,
            control_mode="ControlNet is more important",  # type: ignore
            resize_mode="Crop and Resize",
        )

    def _prepare_cn_depth_model(self, models: List[str], depth_guide: Image.Image):
        depth_model = next((x for x in models if "sd15_depth" in x), None)
        logger.debug(f"{depth_model=}")

        if depth_model is None:
            raise Exception(
                (
                    "Failed to find a proper depth model,"
                    "which contains 'sd15_depth' in its name."
                )
            )

        return webuiapi.ControlNetUnit(
            image=depth_guide,  # type: ignore
            module="depth_midas",
            model=depth_model,
            weight=0.8,
            guidance_end=0.7,
            control_mode="ControlNet is more important",  # type: ignore
            resize_mode="Crop and Resize",
        )

    def _prepare_prompts(
        self,
    ):
        emptiness = 1.0 - (self.num_pieces) / self.total_num_pieces
        empty_plate_weight = f"{emptiness * 1.1:.2f}"
        logger.debug(f"{empty_plate_weight=}")

        half_eaten = "(half eaten:0.5)," if emptiness > 0.5 else ""
        prompt = (
            "pieces of mouthwatering pizza on the plate,"
            f"{half_eaten}"
            f"(empty plate:{empty_plate_weight}),"
            "an incredibly realistic and visually enticing image,"
            "photograph with vibrant colors and textures,"
        )

        neg_prompt = (
            "(worst quality, low quality:1.4),"
            "(low quality, worst quality:1.4),(bad_prompt:0.8),"
            "logo, text, watermark, overcooked, (burnt:1.4), unappealing, disgusting,"
            "poorly-lit and has dull colors, unappetizing, blurry, fruit,"
        )

        return prompt, neg_prompt

    def generate(
        self,
        depth_guide: Optional[Image.Image] = None,
        prompt_override: Optional[str] = None,
        neg_prompt_override: Optional[str] = None,
        seed: int = -1,
    ):
        # Configure ControlNet units
        cn = webuiapi.ControlNetInterface(self.client)
        cn_models: List[str] = cn.model_list()
        logger.debug(f"{cn_models=}")

        # Weaker weight if depth_guide is given
        seg_weight = 1.1 if depth_guide else 3.0
        if self.seg_weight is not None:
            seg_weight = self.seg_weight

        logger.debug(f"{seg_weight=}")
        cn_units = [self._prepare_cn_seg_model(cn_models, seg_weight)]

        if depth_guide:
            cn_units.append(self._prepare_cn_depth_model(cn_models, depth_guide))

        # Prepare prompts
        prompt, neg_prompt = self._prepare_prompts()

        if prompt_override:
            prompt = prompt_override
        if neg_prompt_override:
            neg_prompt = neg_prompt_override
        logger.debug(f"{prompt=}, {neg_prompt=}")

        # Generate image
        with console.status("Processing...", spinner="pong"):
            res = self.client.txt2img(
                prompt=prompt,
                negative_prompt=neg_prompt,
                seed=seed,
                cfg_scale=2.5,
                steps=20,
                width=self.width,
                height=self.width,
                sampler_name="DPM++ 3M SDE",
                controlnet_units=cn_units,
                use_async=False,
            )
            res = cast(webuiapi.WebUIApiResult, res)

        return res.image, res.info
