"""RIGForge Control Plane — Registries, Ownership, Health Checks.

Core law:
    If it is not registered, it does not exist.
    If it has no healthcheck, it is not ready.
    If it has no owner, it is not allowed in production.
    If it has no proof path, it cannot participate in a RIG workflow.
"""
from runtime.control_plane.registry_loader import RegistryLoader, load_all_registries
from runtime.control_plane.registry_validator import RegistryValidator, validate_all_registries
from runtime.control_plane.healthcheck_runner import HealthcheckRunner, check_service
from runtime.control_plane.ownership_validator import OwnershipValidator
from runtime.control_plane.proof_path_validator import ProofPathValidator