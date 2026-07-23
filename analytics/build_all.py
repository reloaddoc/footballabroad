import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analytics import (
    build_agency_networks,
    build_league_flows,
    build_player_archetypes,
    build_stepping_clubs,
    build_transfer_corridors,
)


def build():
    build_transfer_corridors.build()
    build_stepping_clubs.build()
    build_league_flows.build()
    build_agency_networks.build()
    build_player_archetypes.build()


if __name__ == "__main__":
    build()
