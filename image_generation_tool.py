#!/usr/bin/env python3
"""
Image Generation Tools Module

This module provides image generation tools using Google's Gemini 2.5 Flash Image model.
Uses the official google-genai SDK with response_modalities=["IMAGE", "TEXT"].
"""

import json
import logging
import os
import datetime
import uuid
from typing import Dict, Any, Optional
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

from tools.debug_helpers import DebugSession
from tools.registry import registry, tool_error

logger = logging.getLogger(__name__)

# Configuration
DEFAULT_MODEL = "gemini-2.5-flash-image"
DEFAULT_ASPECT_RATIO = "landscape"
DEFAULT_NUM_IMAGES = 1

# Note: Gemini 2.5 Flash Image handles aspect ratios via the prompt
# or internal model logic; the SDK config for generate_content
# doesn't use a simple 'aspect_ratio' string like the dedicated Imagen API.
ASPECT_RATIO_MAP = {
    "landscape": "wide (16:9)",
    "square": "square (1:1)",
    "portrait": "tall (9:16)"
}

STATIC_DIR = "/home/ubuntu/.hermes/hermes-agent/static/generated_images"
BASE_URL = "http://987.654.32.1:8000"   #please amend your
os.makedirs(STATIC_DIR, exist_ok=True)

_debug = DebugSession("image_tools", env_var="IMAGE_TOOLS_DEBUG")

def _generate_gemini_image(prompt: str, aspect_ratio: str) -> Optional[str]:
    """
    Generate an image using the Gemini 2.5 Flash Image model.
    """
    try:
        if genai is None:
            raise ImportError("google-genai SDK not installed. Please run: pip install google-genai")

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")

        client = genai.Client(api_key=api_key)

        # We append the aspect ratio to the prompt to guide the model
        full_prompt = f"{prompt}. Aspect ratio: {aspect_ratio}."

        # The "Get Code" secret: use generate_content with response_modalities=["IMAGE"]
        response = client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )

        if not response or not response.candidates:
            logger.error("Gemini returned no candidates")
            return None

        # Extract the image from the parts of the first candidate
        candidate = response.candidates[0]
        image_bytes = None

        for part in candidate.content.parts:
            if part.inline_data and part.inline_data.data:
                image_bytes = part.inline_data.data
                break

        if not image_bytes:
            logger.error("No image data found in the model response")
            return None

        # Save image to local storage
        filename = f"gen_{uuid.uuid4()}.png"
        filepath = os.path.join(STATIC_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(image_bytes)

        image_url = f"{BASE_URL}/static/generated_images/{filename}"
        logger.info("Image successfully generated and saved to %s", image_url)
        return image_url

    except Exception as e:
        logger.error("Error generating image with Gemini: %s", e, exc_info=True)
        raise e

def image_generate_tool(
    prompt: str,
    aspect_ratio: str = DEFAULT_ASPECT_RATIO,
    num_images: int = DEFAULT_NUM_IMAGES,
    output_format: str = "png",
    seed: Optional[int] = None
) -> str:
    aspect_ratio_lower = aspect_ratio.lower().strip() if aspect_ratio else DEFAULT_ASPECT_RATIO
    gemini_ratio = ASPECT_RATIO_MAP.get(aspect_ratio_lower, ASPECT_RATIO_MAP[DEFAULT_ASPECT_RATIO])

    debug_call_data = {
        "parameters": {"prompt": prompt, "aspect_ratio": aspect_ratio},
        "success": False,
        "generation_time": 0
    }

    start_time = datetime.datetime.now()

    try:
        if not prompt or not isinstance(prompt, str) or len(prompt.strip()) == 0:
            raise ValueError("Prompt is required")

        image_url = _generate_gemini_image(prompt.strip(), gemini_ratio)

        if not image_url:
            raise ValueError("Gemini failed to generate a valid image")

        generation_time = (datetime.datetime.now() - start_time).total_seconds()
        response_data = {"success": True, "image": image_url}

        debug_call_data.update({"success": True, "generation_time": generation_time})
        _debug.log_call("image_generate_tool", debug_call_data)
        _debug.save()

        return json.dumps(response_data, indent=2, ensure_ascii=False)

    except Exception as e:
        generation_time = (datetime.datetime.now() - start_time).total_seconds()
        error_msg = f"Gemini Error: {str(e)}"
        logger.error("%s", error_msg, exc_info=True)

        response_data = {"success": False, "image": None, "error": error_msg}
        debug_call_data.update({"error": error_msg, "generation_time": generation_time})
        _debug.log_call("image_generate_tool", debug_call_data)
        _debug.save()

        return json.dumps(response_data, indent=2, ensure_ascii=False)

def check_image_generation_requirements() -> bool:
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            return False
        import google.genai
        return True
    except ImportError:
        return False

def get_debug_session_info() -> Dict[str, Any]:
    return _debug.get_session_info()

from tools.registry import registry, tool_error

IMAGE_GENERATE_SCHEMA = {
    "name": "image_generate",
    "description": "Generate images using Gemini 2.5 Flash Image. Returns a URL. ![desc](URL)",
    "parameters": {
        "type": "object",
        "properties": {
            "prompt": {"type": "string", "description": "Detailed image description."},
            "aspect_ratio": {
                "type": "string",
                "enum": ["landscape", "square", "portrait"],
                "description": "The aspect ratio of the generated image.",
                "default": "landscape"
            }
        },
        "required": ["prompt"]
    }
}

def _handle_image_generate(args, **kw):
    prompt = args.get("prompt", "")
    if not prompt: return tool_error("prompt is required")
    return image_generate_tool(prompt=prompt, aspect_ratio=args.get("aspect_ratio", "landscape"))

registry.register(
    name="image_generate",
    toolset="image_gen",
    schema=IMAGE_GENERATE_SCHEMA,
    handler=_handle_image_generate,
    check_fn=check_image_generation_requirements,
    requires_env=[],
    is_async=False,
    emoji="🎨",
)
