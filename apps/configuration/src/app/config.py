"""Compatibility wrapper around shared tutor_lib settings."""

from tutor_lib import config as _shared_config

AuthConfig = _shared_config.AuthConfig
AzureAIConfig = _shared_config.AzureAIConfig
CosmosConfig = _shared_config.CosmosConfig
StorageConfig = _shared_config.StorageConfig
TutorSettings = _shared_config.TutorSettings
get_settings = _shared_config.get_settings

__all__ = [
    "AuthConfig",
    "AzureAIConfig",
    "CosmosConfig",
    "StorageConfig",
    "TutorSettings",
    "get_settings",
]
