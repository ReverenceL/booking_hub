from dataclasses import dataclass
from datetime import datetime

from hub.domain.models.client import ClientId
from hub.domain.models.master import MasterId
from hub.domain.new_type import new_type

AppointmentId = int
AppointmentDateTime = datetime


@dataclass
class Appointment:
    id: AppointmentId | None
    date_time: AppointmentDateTime
    master_id: MasterId
    client_id: ClientId
