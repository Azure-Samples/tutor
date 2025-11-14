"""Vision agent toolkit exposing Azure AI Vision and CosmosDB helpers."""

from __future__ import annotations

import asyncio
import base64
import logging
import os
import time
from dataclasses import dataclass
from io import BytesIO
from typing import Any, Optional, Union

import requests
from PIL import Image
from agent_framework.azure import AgentToolkit
from agent_framework.decorators import ai_function
from azure.ai.vision.imageanalysis import ImageAnalysisClient, VisualFeatures
from azure.core.credentials import AzureKeyCredential
from azure.cosmos.aio import CosmosClient


logger = logging.getLogger(__name__)

__all__ = ["VisionSettings", "VisionToolkit", "build_vision_toolkit"]


def _get_env(name: str, *, required: bool = False) -> Optional[str]:
    value = os.getenv(name)
    if required and not value:
        raise AttributeError(f"Missing required environment variable: {name}")
    return value


@dataclass(slots=True)
class VisionSettings:
    """Strongly typed configuration for the vision toolkit."""

    vision_endpoint: str
    vision_key: str
    cosmos_endpoint: Optional[str] = None
    cosmos_key: Optional[str] = None
    cosmos_database: Optional[str] = None
    cosmos_container: Optional[str] = None

    @classmethod
    def from_env(cls) -> "VisionSettings":
        return cls(
            vision_endpoint=_get_env("AZURE_VISION_ENDPOINT", required=True) or "",
            vision_key=_get_env("AZURE_VISION_KEY", required=True) or "",
            cosmos_endpoint=_get_env("COSMOS_VISION_ENDPOINT"),
            cosmos_key=_get_env("COSMOS_KEY"),
            cosmos_database=_get_env("COSMOS_DATABASE"),
            cosmos_container=_get_env("COSMOS_CONTAINER"),
        )


class VisionToolkit:
    """Collection of Azure AI Vision helpers exposed as agent tools."""

    def __init__(self, settings: VisionSettings | None = None) -> None:
        self._settings = settings or VisionSettings.from_env()
        self._vision_credential = AzureKeyCredential(self._settings.vision_key)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _vision_client(self) -> ImageAnalysisClient:
        return ImageAnalysisClient(
            endpoint=self._settings.vision_endpoint,
            credential=self._vision_credential,
        )

    async def _validate_url(self, url: str) -> None:
        def _head() -> None:
            response = requests.head(url, timeout=10)
            response.raise_for_status()

        await asyncio.to_thread(_head)

    async def _download_image(self, url: str) -> bytes:
        def _get() -> bytes:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.content

        return await asyncio.to_thread(_get)

    def _ensure_cosmos(self) -> None:
        if not all(
            [
                self._settings.cosmos_endpoint,
                self._settings.cosmos_key,
                self._settings.cosmos_database,
                self._settings.cosmos_container,
            ]
        ):
            raise AttributeError("Cosmos configuration is incomplete; cannot persist images.")

    # ------------------------------------------------------------------
    # Agent tool definitions
    # ------------------------------------------------------------------
    @ai_function(name="ingest_image", description="Validate that an image URL is reachable.")
    async def ingest_image(self, image_url: str) -> str:
        await self._validate_url(image_url)
        return image_url

    @ai_function(
        name="load_images",
        description="Load images from URLs or byte arrays and return a list of byte buffers.",
    )
    async def load_images(self, image_sources: list[Union[str, bytes]]) -> list[Optional[bytes]]:
        images: list[Optional[bytes]] = []
        for source in image_sources:
            if isinstance(source, str):
                try:  # pragma: no cover - network failures not deterministic
                    await self._validate_url(source)
                    images.append(await self._download_image(source))
                except Exception as exc:  # noqa: BLE001
                    logger.error("Failed to download image '%s': %s", source, exc)
                    images.append(None)
            else:
                images.append(source)
        return images

    @ai_function(name="save_image_set", description="Persist images and metadata into Cosmos DB.")
    async def save_image_set(
        self,
        images: list[Optional[bytes]],
        metadata: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        self._ensure_cosmos()
        assert self._settings.cosmos_endpoint is not None
        assert self._settings.cosmos_key is not None
        assert self._settings.cosmos_database is not None
        assert self._settings.cosmos_container is not None

        results: list[dict[str, Any]] = []
        async with CosmosClient(self._settings.cosmos_endpoint, credential=self._settings.cosmos_key) as client:
            database = client.get_database_client(self._settings.cosmos_database)
            container = database.get_container_client(self._settings.cosmos_container)

            for index, (image_bytes, meta) in enumerate(zip(images, metadata, strict=False)):
                if not image_bytes:
                    continue

                encoded = base64.b64encode(image_bytes).decode("utf-8")
                item = {
                    "id": meta.get("id", f"image-{int(time.time())}-{index}"),
                    "image_base64": encoded,
                    "metadata": meta,
                    "type": "image",
                    "timestamp": time.time(),
                }
                response = await container.upsert_item(item)
                results.append(response)

        return results

    @ai_function(name="add_captions", description="Generate captions for supplied images.")
    async def add_captions(self, images: list[Optional[bytes]]) -> list[dict[str, Any]]:
        captions: list[dict[str, Any]] = []
        async with self._vision_client() as client:
            for image in images:
                if not image:
                    captions.append({"caption": "No image available"})
                    continue
                try:
                    result = await client.analyze(
                        image_data=image,
                        visual_features=[VisualFeatures.CAPTION],
                    )
                    caption_text = getattr(result.caption, "content", None) or getattr(result.caption, "text", "")
                    captions.append(
                        {
                            "caption": caption_text or "No caption generated",
                            "confidence": getattr(result.caption, "confidence", 0.0),
                        }
                    )
                except Exception as exc:  # pragma: no cover - SDK/network error
                    logger.error("Caption generation failed: %s", exc)
                    captions.append({"caption": f"Caption error: {exc}"})
        return captions

    @ai_function(name="extract_tags", description="Extract vision tags and confidences for images.")
    async def extract_tags(self, images: list[Optional[bytes]]) -> list[dict[str, Any]]:
        tag_sets: list[dict[str, Any]] = []
        async with self._vision_client() as client:
            for image in images:
                if not image:
                    tag_sets.append({"tags": []})
                    continue
                try:
                    result = await client.analyze(
                        image_data=image,
                        visual_features=[VisualFeatures.TAGS],
                    )
                    tags = []
                    if result.tags:
                        for tag in result.tags.list:
                            tags.append({"name": tag.get("name"), "confidence": tag.get("confidence")})
                    tag_sets.append({"tags": tags})
                except Exception as exc:  # pragma: no cover
                    logger.error("Tag extraction failed: %s", exc)
                    tag_sets.append({"tags": [], "error": str(exc)})
        return tag_sets

    @ai_function(name="crop_images", description="Crop images around the largest detected object.")
    async def crop_images(self, images: list[Optional[bytes]]) -> list[Optional[bytes]]:
        cropped: list[Optional[bytes]] = []
        async with self._vision_client() as client:
            for image in images:
                if not image:
                    cropped.append(None)
                    continue
                try:
                    original = Image.open(BytesIO(image))
                    result = await client.analyze(
                        image_data=image,
                        visual_features=[VisualFeatures.SMART_CROPS, VisualFeatures.OBJECTS],
                    )
                    objects = [obj for obj in result.objects or [] if hasattr(obj, "bounding_box")]
                    if not objects:
                        cropped.append(image)
                        continue
                    largest = max(
                        objects,
                        key=lambda obj: (max(p.x for p in obj.bounding_box) - min(p.x for p in obj.bounding_box))
                        * (max(p.y for p in obj.bounding_box) - min(p.y for p in obj.bounding_box)),
                    )
                    xs = [point.x for point in largest.bounding_box]
                    ys = [point.y for point in largest.bounding_box]
                    crop_box = (
                        int(min(xs) * original.width),
                        int(min(ys) * original.height),
                        int(max(xs) * original.width),
                        int(max(ys) * original.height),
                    )
                    buffer = BytesIO()
                    original.crop(crop_box).save(buffer, format="PNG")
                    cropped.append(buffer.getvalue())
                except Exception as exc:  # pragma: no cover
                    logger.error("Image crop failed: %s", exc)
                    cropped.append(image)
        return cropped

    @ai_function(name="extract_text", description="Run OCR over an image (bytes or URL).")
    async def extract_text(self, image: Union[str, bytes]) -> dict[str, Any]:
        async with self._vision_client() as client:
            try:
                if isinstance(image, str):
                    await self._validate_url(image)
                    result = await client.analyze_from_url(
                        image_url=image,
                        visual_features=[VisualFeatures.READ],
                    )
                else:
                    result = await client.analyze(
                        image_data=image,
                        visual_features=[VisualFeatures.READ],
                    )
            except Exception as exc:  # pragma: no cover
                logger.error("OCR failed: %s", exc)
                raise ValueError(f"Failed to extract text from image: {exc}") from exc

        regions: list[dict[str, Any]] = []
        read_section = getattr(result, "read", None)
        if read_section and getattr(read_section, "blocks", None):
            for block in read_section.blocks:
                if not getattr(block, "lines", None):
                    continue
                for line in block.lines:
                    text = getattr(line, "content", None) or getattr(line, "text", "")
                    if not text:
                        continue
                    polygon = getattr(line, "bounding_polygon", None) or []
                    if polygon:
                        xs = [point.x for point in polygon]
                        ys = [point.y for point in polygon]
                        regions.append(
                            {
                                "text": text,
                                "bounding_box": {
                                    "x": min(xs),
                                    "y": min(ys),
                                    "width": max(xs) - min(xs),
                                    "height": max(ys) - min(ys),
                                },
                                "confidence": getattr(line, "confidence", 0.0),
                            }
                        )
                    else:
                        regions.append({"text": text, "confidence": getattr(line, "confidence", 0.0)})

        combined_text = " ".join(region.get("text", "") for region in regions).strip()
        language = getattr(read_section, "language", "unknown") if read_section else "unknown"
        return {"text": combined_text, "regions": regions, "language": language}

    @ai_function(name="detect_objects", description="Detect objects present in an image byte buffer.")
    async def detect_objects(self, image: bytes) -> dict[str, Any]:
        async with self._vision_client() as client:
            try:
                result = await client.analyze(
                    image_data=image,
                    visual_features=[VisualFeatures.OBJECTS],
                )
            except Exception as exc:  # pragma: no cover
                logger.error("Object detection failed: %s", exc)
                return {"objects": [], "count": 0, "error": str(exc)}

        objects = []
        for obj in result.objects or []:
            xs = [point.x for point in obj.bounding_box]
            ys = [point.y for point in obj.bounding_box]
            objects.append(
                {
                    "name": obj.name,
                    "confidence": obj.confidence,
                    "bounding_box": {
                        "x": min(xs),
                        "y": min(ys),
                        "width": max(xs) - min(xs),
                        "height": max(ys) - min(ys),
                    },
                }
            )
        return {"objects": objects, "count": len(objects)}


def build_vision_toolkit(settings: VisionSettings | None = None) -> AgentToolkit:
    """Create an `AgentToolkit` bundling the vision tools for registration."""

    toolkit = VisionToolkit(settings=settings)
    return AgentToolkit(
        tools=[
            toolkit.ingest_image,
            toolkit.load_images,
            toolkit.save_image_set,
            toolkit.add_captions,
            toolkit.extract_tags,
            toolkit.crop_images,
            toolkit.extract_text,
            toolkit.detect_objects,
        ]
    )
