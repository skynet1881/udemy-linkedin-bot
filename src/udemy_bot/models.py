from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CourseConfig:
    course_id: str
    course_label: str
    udemy_promotions_url: str
    coupon_prefix: str
    coupon_price: str
    monthly_coupon_limit: int
    max_redemptions: int
    linkedin_message_template: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CourseConfig":
        return cls(
            course_id=data["course_id"],
            course_label=data["course_label"],
            udemy_promotions_url=data["udemy_promotions_url"],
            linkedin_message_template=data["linkedin_message_template"],

            coupon_prefix=data.get("coupon_prefix", "DISC"),
            coupon_price=str(data.get("coupon_price", 9.99)),
            monthly_coupon_limit=int(data.get("monthly_coupon_limit", 3)),
            max_redemptions=int(data.get("max_redemptions", 1000)),
            
        )


@dataclass(frozen=True)
class CouponResult:
    coupon_code: str
    coupon_url: str


@dataclass(frozen=True)
class CourseDecision:
    course: CourseConfig
    reason: str
