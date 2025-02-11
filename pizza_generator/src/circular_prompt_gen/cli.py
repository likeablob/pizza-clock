import json
from pathlib import Path
from typing import List

import typer
from ollama import Client
from pydantic import BaseModel

from pizza_gen.logger import get_logger  # TODO: use a proper logger

logger = get_logger(__name__)

app = typer.Typer()


class Prompt(BaseModel):
    thing: str
    prompt: str


output_examples = [
    {
        "thing": "soap bubble",
        "prompt": "A photorealistic, close-up photograph of a single, iridescent soap bubble floating in mid-air. The spherical bubble reflects a rainbow of colors, showcasing its thin, delicate film. The background is a softly blurred, green garden. Gentle, natural sunlight illuminates the bubble from the side, creating highlights and subtle shadows. The atmosphere is peaceful and serene. The bubble's surface has a smooth, glassy texture.",
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
2.  **Focus on Circular Shape:** The prompt must describe a single, specific object, emphasizing its circular or round shape.
3.  **Detailed Description:**  Provide a detailed description of the object, including its texture, material, color, and any relevant details that contribute to its visual appearance.
4.  **Viewpoint/Angle:** If the viewing angle (e.g., bird's-eye view, close-up, from below) is crucial to capturing the circular shape, specify it clearly in the prompt.
5.  **No Imperative Forms:** Avoid using commands or imperative verbs (e.g., "Create," "Generate," "Make").  Describe the scene as it *is*.
6.  **Singular Noun:** The object name must be a singular noun.
7.  **Lighting and Atmosphere:** Describe the lighting conditions (e.g., soft, bright, dim, natural light, studio lighting) and the overall atmosphere or mood (e.g., serene, dramatic, mysterious).
8.  **Photorealistic Style:** The generated image should be a photorealistic photograph.
9.  **Output Format:** The output must be a JSON object with "thing" and "prompt" keys.
10. **Prohibited Items:** Do not generate a prompt for the following items: {blocklist}
"""


def generate_base_prompt(blocklist: List[str]):
    return base_prompt.format(blocklist=",".join(blocklist))


@app.command()
def genearte(
    ollama_server_url: str = typer.Option(
        "http://127.0.0.1:11434", "-s", "--ollama-server-url"
    ),
    model: str = typer.Option("gemma2:9b", "-m", "--model"),
    num_prompts: int = typer.Option(3, "-n", "--num-prompts"),
    output_file_path: Path = typer.Option(
        "circular_things.json", "-o", "--output-file-path"
    ),
    # Others
    debug: bool = typer.Option(
        False, "--debug", is_flag=True, help="Enable debugging outputs"
    ),
):
    client = Client(host=ollama_server_url)

    outputs = []
    blocklist = ["clock", "watch", "person"]
    for i in range(num_prompts):
        response = client.chat(
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
            format=Prompt.model_json_schema(),
        )
        if response.message.content is None:
            logger.error("Failed to get content. Skipping.")
            continue

        prompt = Prompt.model_validate_json(response.message.content)
        logger.info(prompt)
        outputs.append(prompt)
        blocklist.append(prompt.thing)

    with output_file_path.open("w") as fp:
        json.dump([dict(x) for x in outputs], fp, ensure_ascii=False)
