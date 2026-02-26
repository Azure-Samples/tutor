"""Compatibility wrapper around shared tutor_lib Cosmos helpers."""

from tutor_lib import cosmos as _shared_cosmos

CosmosCRUD = _shared_cosmos.CosmosCRUD

__all__ = ["CosmosCRUD"]
