"""seed the clinic's starting doctor roster

Revision ID: 0002_seed_doctors
"""

import sqlalchemy as sa

from alembic import op

revision = "0002_seed_doctors"
down_revision = "0001_create_doctors_appointments"
branch_labels = None
depends_on = None

SEED_DOCTORS = [
    {"name": "Dr. Ananya Rao", "specialty": "General Medicine", "room": "101"},
    {"name": "Dr. Vikram Mehta", "specialty": "Cardiology", "room": "204"},
    {"name": "Dr. Sara Khan", "specialty": "Pediatrics", "room": "110"},
    {"name": "Dr. Rohan Iyer", "specialty": "Dermatology", "room": "305"},
]


def upgrade():
    doctors = sa.table(
        "doctors", sa.column("name", sa.String), sa.column("specialty", sa.String), sa.column("room", sa.String)
    )
    op.bulk_insert(doctors, SEED_DOCTORS)


def downgrade():
    names = [d["name"] for d in SEED_DOCTORS]
    op.execute(
        sa.text("DELETE FROM doctors WHERE name IN :names").bindparams(
            sa.bindparam("names", value=names, expanding=True)
        )
    )
