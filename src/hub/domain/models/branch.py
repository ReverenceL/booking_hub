from dataclasses import dataclass

from hub.domain.models.city import CityId
from hub.domain.new_type import new_type

BranchId = new_type("BranchId", int)
BranchName = new_type("BranchName", str)
BranchAddress = new_type("BranchAddress", str)


@dataclass
class Branch:
    id: BranchId | None
    name: BranchName
    address: BranchAddress

    city_id: CityId


@dataclass
class AvailableBranch(Branch):
    is_associated: bool
