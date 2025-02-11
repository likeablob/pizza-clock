from typing import List, Optional, cast
from urllib.parse import urlparse

import webuiapi
from PIL import Image, ImageDraw

from pizza_gen.logger import console, get_logger

logger = get_logger(__name__)


class CircularGen:
    def __init__(
        self,
        server_url: str,
        width: int,
        canny_weight: Optional[float] = None,
        debug: bool = False,
    ) -> None:
        self.client = self._create_client(server_url)
        self.width = width
        self.canny_weight = canny_weight
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

    def _prepare_canny_image(self):
        image_size = (self.width, self.width)

        im = Image.new("RGBA", image_size, "white")
        draw = ImageDraw.Draw(im)

        circle_d = image_size[0] * 0.90
        circle_padding = (image_size[0] - circle_d) / 2

        # Draw a circle
        draw.ellipse(
            (
                (circle_padding, circle_padding),
                (image_size[0] - circle_padding, image_size[1] - circle_padding),
            ),
            # The "DISH" class is not suitable for rendering an empty dish
            fill="black",
            outline="white",
            width=0,
        )

        if self.debug:
            logger.debug("Saving canny_image to debug_canny_image.png")
            im.save("debug_canny_image.png")

        return im

    def _prepare_cn_canny_model(self, models: List[str], weight: float):
        guide_image = self._prepare_canny_image()

        model = next((x for x in models if "sd15_canny" in x), None)
        logger.debug(f"{model=}")

        if model is None:
            raise Exception(
                (
                    "Failed to find a proper canny model,"
                    "which contains 'sd15_canny' in its name."
                )
            )

        return webuiapi.ControlNetUnit(
            image=guide_image,  # type: ignore
            module="none",
            model=model,
            weight=weight,
            guidance_end=0.65,
            control_mode="ControlNet is more important",  # type: ignore
            resize_mode="Crop and Resize",
        )

    def _prepare_prompts(
        self,
    ):
        neg_prompt = (
            "(worst quality, low quality:1.4),"
            "(low quality, worst quality:1.4),(bad_prompt:0.8),"
            "logo, text, watermark, unappealing, disgusting,"
            "illustration, human, human_face,"
        )

        return neg_prompt

    def generate(
        self,
        prompt: str,
        neg_prompt_override: Optional[str] = None,
        seed: int = -1,
    ):
        # Configure ControlNet units
        cn = webuiapi.ControlNetInterface(self.client)
        cn_models: List[str] = cn.model_list()
        logger.debug(f"{cn_models=}")

        canny_weight = 0.60
        if self.canny_weight is not None:
            canny_weight = self.canny_weight

        logger.debug(f"{canny_weight=}")
        cn_units = [self._prepare_cn_canny_model(cn_models, canny_weight)]

        # Prepare prompts
        neg_prompt = self._prepare_prompts()

        if neg_prompt_override:
            neg_prompt = neg_prompt_override
        logger.debug(f"{prompt=}, {neg_prompt=}")

        # Generate image
        with console.status("Processing...", spinner="pong"):
            res = self.client.txt2img(
                prompt=prompt,
                negative_prompt=neg_prompt,
                seed=seed,
                cfg_scale=10,
                steps=20,
                width=self.width,
                height=self.width,
                sampler_name="Euler a",
                controlnet_units=cn_units,
                use_async=False,
            )
            res = cast(webuiapi.WebUIApiResult, res)

        return res.image, res.info
