"""Business metrics exported next to the HTTP metrics on /metrics."""

from prometheus_client import Counter

APPOINTMENTS_BOOKED = Counter(
    "clinicflow_appointments_booked_total",
    "Appointments booked, by doctor specialty",
    ["specialty"],
)

APPOINTMENT_STATUS_CHANGES = Counter(
    "clinicflow_appointment_status_changes_total",
    "Appointment status transitions, by new status",
    ["status"],
)
