"""
Gemini API demo with streaming responses.
"""

import base64
from openai import OpenAI

# Config
BASE_URL = "http://127.0.0.1:8000/v1"
API_KEY = "sk-geminixxxxx"

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)


def load_image_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def print_stream(stream) -> None:
    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        if delta and getattr(delta, "content", None):
            print(delta.content, end="", flush=True)
    print()


def chat_text() -> None:
    print("=" * 50)
    print("Text chat (stream)")
    print("=" * 50)

    stream = client.chat.completions.create(
        model="gemini-3.0-pro",
        messages=[{"role": "user", "content": "你好，介绍一下你自己"}],
        stream=True,
    )
    print_stream(stream)


def chat_single_image() -> None:
    print("\n" + "=" * 50)
    print("Single image (stream)")
    print("=" * 50)

    img_b64 = load_image_base64("image.png")

    stream = client.chat.completions.create(
        model="gemini-3.0-flash",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "描述这张图片"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
                ],
            }
        ],
        stream=True,
    )
    print_stream(stream)


def chat_multi_images() -> None:
    print("\n" + "=" * 50)
    print("Multi image (stream)")
    print("=" * 50)

    img1_b64 = load_image_base64("a.png")
    img2_b64 = load_image_base64("b.png")

    stream = client.chat.completions.create(
        model="gemini-3.0-pro",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "比较这两张图片的区别"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img1_b64}"}},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img2_b64}"}},
                ],
            }
        ],
        stream=True,
    )
    print_stream(stream)


def chat_image_generation() -> None:
    print("\n" + "=" * 50)
    print("Image generation (stream)")
    print("=" * 50)

    stream = client.chat.completions.create(
        model="gemini-3.0-pro",
        messages=[{"role": "user", "content": "生成一张可爱的猫咪图片"}],
        stream=True,
    )
    print_stream(stream)


if __name__ == "__main__":
    chat_text()

    # Uncomment as needed:
    # chat_single_image()
    # chat_multi_images()
    # chat_image_generation()
