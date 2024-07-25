from dataclasses import dataclass

from hub.domain.models.master import MasterId
from hub.domain.models.service import ServiceId
from hub.domain.new_type import new_type

WorkTime = new_type("WorkTime", int)
BreakTime = new_type("BreakTime", int)


@dataclass
class ServiceMaster:
    work_time: WorkTime
    break_time: BreakTime

    service_id: ServiceId
    master_id: MasterId
