from __future__ import annotations

from .models import CourseConfig


def build_coupon_code(course: CourseConfig, serial: int) -> str:
    return f"{course.coupon_prefix}-{serial:04d}"


def render_linkedin_message(course: CourseConfig, coupon_url: str) -> str:
    return course.linkedin_message_template.format(
        course_id=course.course_id,
        course_label=course.course_label,
        coupon_url=coupon_url,
    )
