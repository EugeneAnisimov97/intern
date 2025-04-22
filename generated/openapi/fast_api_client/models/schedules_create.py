from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SchedulesCreate")


@_attrs_define
class SchedulesCreate:
    """
    Attributes:
        medicine (str):
        periodicity (int):
        duration (Union[None, int]):
        user_id (int):
    """

    medicine: str
    periodicity: int
    duration: Union[None, int]
    user_id: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        medicine = self.medicine

        periodicity = self.periodicity

        duration: Union[None, int]
        duration = self.duration

        user_id = self.user_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "medicine": medicine,
                "periodicity": periodicity,
                "duration": duration,
                "user_id": user_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        medicine = d.pop("medicine")

        periodicity = d.pop("periodicity")

        def _parse_duration(data: object) -> Union[None, int]:
            if data is None:
                return data
            return cast(Union[None, int], data)

        duration = _parse_duration(d.pop("duration"))

        user_id = d.pop("user_id")

        schedules_create = cls(
            medicine=medicine,
            periodicity=periodicity,
            duration=duration,
            user_id=user_id,
        )

        schedules_create.additional_properties = d
        return schedules_create

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
