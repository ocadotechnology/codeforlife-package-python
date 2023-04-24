from ...interactables.pickups.artefacts import (
    ChestArtefact,
    KeyArtefact,
    YellowOrbArtefact,
    PhoneArtefact,
    KeyboardArtefact,
    CoinsArtefact,
)
from ...interactables.pickups.damage_boost_pickup import DamageBoostPickup
from ...interactables.pickups.health_pickup import HealthPickup
from ...interactables.pickups.invulnerability_pickup import (
    InvulnerabilityPickup,
)


def serialize_pickups(world_map):
    return [cell.interactable.serialize() for cell in world_map.pickup_cells()]


ALL_PICKUPS = (
    DamageBoostPickup,
    InvulnerabilityPickup,
    HealthPickup,
    YellowOrbArtefact,
    ChestArtefact,
    KeyArtefact,
    PhoneArtefact,
    KeyboardArtefact,
    CoinsArtefact,
)
