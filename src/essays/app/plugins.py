"""
This module provides advanced image processing capabilities for multi-modal applications by integrating
Azure AI Vision with Azure CosmosDB and Azure AI Search. It supports image content detection,
face recognition, OCR, object detection, and embedding generation for images.

Classes:
    ImageProcessor:
        Handles image file encoding and performs content detection, face recognition, OCR, 
        and object detection with Azure AI Vision SDK.
    ImageEmbedder:
        Generates image embeddings from images and persists results to CosmosDB and Azure AI Search.
    ImageAnswer:
        Applies load, save and frame images for better and complementary usage of vision models.

Dependencies:
    - azure-ai-vision
    - azure-cosmos
    - azure-search-documents
    - azure-identity
    - requests
    - numpy
    - PIL
"""

import os
import time
import logging
import base64
import requests

from dotenv import load_dotenv

from typing import Any, Union
from io import BytesIO
from PIL import Image

from azure.ai.vision.imageanalysis.aio import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from azure.cosmos.aio import CosmosClient

from semantic_kernel.functions.kernel_function_decorator import kernel_function


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_FILE = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_FILE)


logger = logging.getLogger(__name__)


AZURE_VISION_ENDPOINT = os.getenv("AZURE_VISION_ENDPOINT", "")
AZURE_VISION_KEY = os.getenv("AZURE_VISION_KEY", "")


class ImageProcessor:
    """
    Handles image file encoding and performs content detection as well as face recognition, 
    OCR and object detection with Azure AI Vision SDK.
    """

    def __init__(self):
        """
        Initialize the ImageProcessor with an Azure AI Vision key and endpoint.
        
        Args:
            key (str): The Azure AI Vision subscription key.
            endpoint (str): The endpoint URL for Azure AI Vision service.
        """
        self.vision_client = ImageAnalysisClient(
            endpoint=AZURE_VISION_ENDPOINT,
            credential=AzureKeyCredential(AZURE_VISION_KEY)
        )

    @kernel_function(name="IngestImage", description="Validates and returns the image URL for downstream processing")
    async def ingest_image(self, image_url: str) -> str:
        """
        Ingest an image from a URL and convert it to bytes.
        
        Args:
            image_url (str): URL of the image to ingest.
            
        Returns:
            bytes: The image content as bytes.
            
        Raises:
            Exception: If the image cannot be retrieved or processed.
        """
        try:
            # Validate URL reachable
            response = requests.head(image_url, timeout=10)
            response.raise_for_status()
            return image_url
        except Exception as e:
            logger.error("Error validating image URL: %s", e)
            raise AttributeError(f"Invalid image URL: {e}") from e

    @kernel_function(name="LoadImages", description="Loads multiple images from URLs or byte arrays")
    async def load_images(self, image_sources: list[Union[str, bytes]]) -> list[bytes]:
        """
        Load multiple images from various sources (URLs or bytes) into an array of bytes.
        
        Args:
            image_sources (list[Union[str, bytes]]): list of image URLs or byte arrays.
            
        Returns:
            list[bytes]: list of images as byte arrays.
        """
        images = []
        for source in image_sources:
            try:
                if isinstance(source, str):
                    image_bytes = await self.ingest_image(source)
                else:
                    image_bytes = source
                images.append(image_bytes)
            except Exception as e:
                logger.error("Error loading image: %s", e)
                images.append(None)
        return images

    @kernel_function(name="SaveImageSet", description="Saves a set of images with metadata to the database")
    async def save_image_set(self, images: list[bytes], metadata: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Save a set of images with their metadata to the database.


        Args:
            images (list[bytes]): list of images as bytes.
            metadata (list[dict[str, Any]]): list of metadata for each image.


        Returns:
            list[dict[str, Any]]: list of responses from the database.
        """
        try:
            cosmos_endpoint = os.environ.get("COSMOS_VISION_ENDPOINT", "")
            cosmos_key = os.environ.get("COSMOS_KEY", AZURE_VISION_KEY)
            cosmos_endpoint = os.environ.get("COSMOS_VISION_ENDPOINT", "")
            cosmos_key = os.environ.get("COSMOS_KEY", AZURE_VISION_KEY)
            database_name = os.environ.get("COSMOS_DATABASE", "")
            container_name = os.environ.get("COSMOS_CONTAINER", "")

            client = CosmosClient(cosmos_endpoint, credential=cosmos_key)
            database = client.get_database_client(database_name)
            container = database.get_container_client(container_name)

            results = []
            for i, (image_bytes, meta) in enumerate(zip(images, metadata)):
                if image_bytes is None:
                    continue

                encoded = base64.b64encode(image_bytes).decode('utf-8')
                item = {
                    "id": meta.get("id", f"image-{int(time.time())}-{i}"),
                    "image_base64": encoded,
                    "metadata": meta,
                    "type": "image",
                    "timestamp": time.time()
                }

                response = await container.upsert_item(item)
                results.append(response)

            return results

        except Exception as e:
            logger.error("Error saving image set: %s", e)
            raise AttributeError(f"Failed to save image set: {str(e)}") from e

    @kernel_function(name="AddCaptions", description="Uses Azure AI Vision to add captions to images")
    async def add_captions(self, images: list[bytes]) -> list[dict[str, str]]:
        """
        Uses Azure AI Vision SDK to add captions to images.

        Args:
            images (list[bytes): list of images as bytes.

        Returns:
            list[dict[str, str]]: list of captions for each image.
        """
        captions = []

        async with self.vision_client as client:
            for image in images:
                if image is None:
                    captions.append({"caption": "No image available"})
                    continue

                try:
                    analysis_result= await client.analyze(
                        image_data=image,
                        visual_features=[VisualFeatures.CAPTION]
                    )
                    if hasattr(analysis_result, 'caption') and analysis_result.caption:
                        captions.append({
                            "caption": analysis_result.caption.text,  # Use .content instead of .text
                            "confidence": analysis_result.caption.confidence
                        })
                    else:
                        captions.append({"caption": "No caption generated"})

                except Exception as e:
                    logger.error("Error generating caption: %s", e)
                    captions.append({"caption": f"Caption error: {str(e)}"})

        return captions

    @kernel_function(name="ExtractTags", description="Extracts tags from images using Azure AI Vision")
    async def extract_tags(self, images: list[bytes]) -> list[dict[str, Any]]:
        """
        Uses Azure AI Vision SDK to extract tags from images.
        
        Args:
            images (list[bytes]): list of images as bytes.
            
        Returns:
            list[dict[str, Any]]: list of tag sets for each image.
        """
        all_tags = []
        async with self.vision_client as client:
            for image in images:
                if image is None:
                    all_tags.append({"tags": []})
                    continue

                try:
                    result= await client.analyze(
                        image_data=image,
                        visual_features=[VisualFeatures.TAGS]
                    )

                    tags = []
                    if result.tags:
                        for tag in result.tags.list:
                            tags.append({
                                "name": tag.get("name"),
                                "confidence": tag.get("confidence")
                            })

                    all_tags.append({"tags": tags})

                except Exception as e:
                    logger.error("Error extracting tags: %s", e)
                    all_tags.append({"tags": [], "error": str(e)})

        return all_tags

    @kernel_function(name="CropImages", description="Crops images to their region of interest")
    async def crop_images(self, images: list[bytes]) -> list[bytes]:
        """
        Uses Azure AI Vision SDK to crop images to the region of interest.
        
        Args:
            images (list[bytes]): list of images as bytes.
            
        Returns:
            list[bytes]: list of cropped images.
        """
        cropped_images = []

        for image in images:
            if image is None:
                cropped_images.append(None)
                continue

            try:
                image_data = Image.open(image)
                original_size = image_data.size
                result = await self.vision_client.analyze(
                    image_data=image,
                    visual_features=[VisualFeatures.SMART_CROPS, VisualFeatures.OBJECTS]
                )

                if result.objects and len(result.objects) > 0:
                    valid_objects = [obj for obj in result.objects if hasattr(obj, 'bounding_box')]
                    largest_object = max(valid_objects, key=lambda x: (max(p.x for p in x.bounding_box) - min(p.x for p in x.bounding_box)) * (max(p.y for p in x.bounding_box) - min(p.y for p in x.bounding_box)))
                    bbox = largest_object.bounding_box
                    x_coords = [p.x for p in bbox]
                    y_coords = [p.y for p in bbox]
                    min_x, max_x = min(x_coords), max(x_coords)
                    min_y, max_y = min(y_coords), max(y_coords)

                    crop_box = (
                        int(min_x * original_size[0]),
                        int(min_y * original_size[1]),
                        int(max_x * original_size[0]),
                        int(max_y * original_size[1])
                    )
                    cropped = image_data.crop(crop_box)

                    buffer = BytesIO()
                    cropped.save(buffer, format="PNG")
                    cropped_images.append(buffer.getvalue())
                else:
                    cropped_images.append(image)

            except Exception as e:
                logger.error("Error cropping image: %s", e)
                cropped_images.append(image)

        return cropped_images


class ImageAnswer:
    """
    Applies load, save, and frame images for better and complementary usage of vision models.
    """

    def __init__(self):
        """
        Initialize the ImageAnswer with an Azure AI Vision key and endpoint.
        
        Args:
            key (str): The Azure AI Vision subscription key.
            endpoint (str): The endpoint URL for Azure AI Vision service.
        """
        self.vision_client = ImageAnalysisClient(
            endpoint=AZURE_VISION_ENDPOINT,
            credential=AzureKeyCredential(AZURE_VISION_KEY)
        )

    @kernel_function(name="ExtractText", description="Extracts text from image bytes or via URL using OCR")
    async def extract_text(self, image: Union[str, bytes]) -> dict[str, Any]:
        """
        Uses Azure AI Vision SDK to detect image text with OCR and adds it to the image data.

        Args:
            image (bytes): The image content as bytes.

        Returns:
            dict[str, Any]: dictionary containing extracted text and related metadata.
        """
        try:
            # Handle URL or bytes: always pass bytes to analyze
            if isinstance(image, str):
                result = await self.vision_client.analyze_from_url(
                    image_url=image,
                    visual_features=[VisualFeatures.READ]
                )
            else:
                result = await self.vision_client.analyze(
                    image_data=image,
                    visual_features=[VisualFeatures.READ]
                )

            extracted_text = ""
            text_regions = []

            if hasattr(result, 'read') and result.read:
                if hasattr(result.read, 'blocks') and result.read.blocks:
                    for block in result.read.blocks:
                        if hasattr(block, 'lines') and block.lines:
                            for line in block.lines:
                                line_text = line.text if hasattr(line, 'text') else ""
                                if line_text:
                                    extracted_text += line_text + " "
                                if hasattr(line, 'bounding_polygon') and line.bounding_polygon:
                                    bbox = line.bounding_polygon
                                    if isinstance(bbox, list) and all(hasattr(point, 'x') for point in bbox):
                                        x_coords = [point.x for point in bbox]
                                        y_coords = [point.y for point in bbox]
                                        min_x, max_x = min(x_coords), max(x_coords)
                                        min_y, max_y = min(y_coords), max(y_coords)
                                        text_regions.append({
                                            "text": line_text,
                                            "bounding_box": {
                                                "x": min_x,
                                                "y": min_y,
                                                "width": max_x - min_x,
                                                "height": max_y - min_y
                                            },
                                            "confidence": 0.0
                                        })

                language = "unknown"

                return {
                    "text": extracted_text.strip(),
                    "regions": text_regions,
                    "language": language
                }
            return {
                "text": "",
                "regions": [],
                "language": "unknown"
            }

        except Exception as e:
            logger.error("Error extracting text: %s", e)
            raise ValueError(f"Failed to extract text from image: {str(e)}") from e

    @kernel_function(name="DetectObjects", description="Detects and identifies objects in images")
    async def detect_objects(self, image: bytes) -> dict[str, Any]:
        """
        Uses Azure AI Vision SDK to detect objects in an image.
        
        Args:
            image (bytes): The image content as bytes.
            
        Returns:
            dict[str, Any]: dictionary containing detected objects and related metadata.
        """
        try:
            result = await self.vision_client.analyze(
                image_data=image,
                visual_features=[VisualFeatures.OBJECTS]
            )
            
            # Extract objects
            objects = []
            
            if result.objects:
                for obj in result.objects:
                    x_coords = [p.x for p in obj.bounding_box]
                    y_coords = [p.y for p in obj.bounding_box]
                    x_val = min(x_coords)
                    y_val = min(y_coords)
                    width_val = max(x_coords) - x_val
                    height_val = max(y_coords) - y_val
                    objects.append({
                        "name": obj.name,
                        "confidence": obj.confidence,
                        "bounding_box": {
                            "x": x_val,
                            "y": y_val,
                            "width": width_val,
                            "height": height_val
                        }
                    })
            
            return {
                "objects": objects,
                "count": len(objects)
            }
            
        except Exception as e:
            logger.error("Error detecting objects: %s", e)
            return {"objects": [], "count": 0, "error": str(e)}
