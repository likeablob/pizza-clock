import json
from pathlib import Path
from typing import List

import typer
from litellm import Choices, completion
from litellm.types.utils import ModelResponse
from pydantic import BaseModel

from pizza_gen.logger import get_logger  # TODO: use a proper logger

logger = get_logger(__name__)

app = typer.Typer()


class Prompt(BaseModel):
    thing: str
    prompt: str


output_examples = [
    {
        "thing": "marble",
        "prompt": "A highly detailed, photorealistic image of a single, perfectly round, polished onyx marble. The marble rests on a smooth, dark wooden surface, illuminated by soft, diffused natural light. The lighting creates a gentle, subtle highlight on the top curve of the sphere, emphasizing its smoothness and perfect circular form. The onyx has subtle, swirling white veins, captured in sharp detail. The background is slightly blurred, emphasizing the crisp focus on the marble. The overall atmosphere is serene and minimalistic. Shot from a slightly elevated angle, the viewer looks down upon the marble, showcasing its three-dimensional roundness.",
    },
    {
        "thing": "ferris wheel",
        "prompt": "A photorealistic, wide-angle shot of a large, illuminated ferris wheel at night. The circular structure is brightly lit with colorful lights, showcasing its intricate design and towering height. The shot is taken from a low angle, emphasizing the scale and grandeur of the wheel against a dark, starry sky. The long exposure captures the motion blur of the lights as the wheel slowly rotates. The overall atmosphere is vibrant and festive.",
    },
]


base_prompt = """
Generate a high-quality image generation prompt for Stable Diffusion, with at least 20 words, formatted as a JSON object.

Rules:

1.  **Clarity and Simplicity:** Use clear, concise, and non-abstract English words. Sentences should be short and easily understood.
2. **Focus on Circular Appearance:** The prompt must describe a single, specific object.  The final depiction of the object in the image *must* appear as a near-perfect circle or a perfect circle. This circular appearance can result from the object's inherent shape, the chosen viewpoint, or a combination of both. The object itself does not need to be inherently round.
3.  **Detailed Description:**  Provide a detailed description of the object, including its texture, material, color, and any relevant details that contribute to its visual appearance.
4. **Viewpoint/Angle:** Specify the viewing angle (e.g., bird's-eye view, close-up, from below) if it is crucial to achieving the circular appearance. If a specific angle is required to perceive the object as circular, it *must* be included.
5.  **No Imperative Forms:** Avoid using commands or imperative verbs (e.g., "Create," "Generate," "Make").  Describe the scene as it *is*.
6.  **Singular Noun:** The object name must be a singular noun.
7.  **Lighting and Atmosphere:** Describe the lighting conditions (e.g., soft, bright, dim, natural light, studio lighting) and the overall atmosphere or mood (e.g., serene, dramatic, mysterious).
8.  **Photorealistic Style:** The generated image should be a photorealistic photograph.
9.  **Output Format:** The output must be a JSON object with "thing" and "prompt" keys.
10. **Circular Composition:** The object should be composed in such a way that its circularity is the dominant visual feature. The prompt should emphasize aspects of the scene that contribute to this circular composition.
11. **Prohibited Items:** Do not generate a prompt for the following items nor similar items: {blocklist}
12. **Positive and Appealing Imagery:** The subject matter and its depiction must be generally perceived as positive, appealing, and suitable for a broad audience.  Avoid anything that could be considered disturbing, frightening, disgusting, gruesome, or otherwise offensive.  Specifically, do not include insects, spiders, webs, decay, bodily fluids, weapons, violence, or anything associated with harm or distress.
"""


def generate_base_prompt(blocklist: List[str]):
    return base_prompt.format(blocklist=",".join(blocklist))


@app.command()
def genearte(
    model: str = typer.Option("ollama_chat/gemma2:9b", "-m", "--model"),
    num_prompts: int = typer.Option(3, "-n", "--num-prompts"),
    output_file_path: Path = typer.Option(
        "circular_things.json", "-o", "--output-file-path"
    ),
    temperature: float = typer.Option(0.7, "-t", "--temperature"),
    # Others
    debug: bool = typer.Option(
        False, "--debug", is_flag=True, help="Enable debugging outputs"
    ),
):
    outputs = []
    blocklist = [
        "clock",
        "watch",
        "person",
    ]
    for i in range(num_prompts):
        response = completion(
            messages=[
                {
                    "role": "user",
                    "content": generate_base_prompt(blocklist),
                },
                *[
                    {
                        "role": "user",
                        "content": f"Example: {json.dumps(x, ensure_ascii=False)}",
                    }
                    for x in output_examples
                ],
            ],
            model=model,
            response_format=Prompt,
            temperature=temperature,
            num_retries=100,
            retry_strategy="exponential_backoff_retry",
        )

        if not isinstance(response, ModelResponse):
            continue
        if not isinstance(response.choices[0], Choices):
            continue
        if response.choices[0].message.content is None:
            logger.error("Failed to get content. Skipping.")
            continue

        prompt = Prompt.model_validate_json(response.choices[0].message.content)
        logger.info(prompt)
        outputs.append(prompt)
        blocklist.append(prompt.thing)

        with output_file_path.open("w") as fp:
            json.dump([dict(x) for x in outputs], fp, ensure_ascii=False)
