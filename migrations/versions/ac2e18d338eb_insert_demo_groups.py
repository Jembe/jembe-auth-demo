"""insert demo groups

Revision ID: ac2e18d338eb
Revises: 39bcbf0bee9a
Create Date: 2021-03-11 14:25:58.199414

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac2e18d338eb'
down_revision = '39bcbf0bee9a'
branch_labels = None
depends_on = None


def upgrade():
    meta = sa.MetaData(bind=op.get_bind())
    meta.reflect(only=('groups',))
    groups = sa.Table('groups', meta)

    # insert records
    op.bulk_insert(
        groups,
        [
            dict(
                id=1,
                name="sysadmin",
                title="System Administrators",
                description=None
            ),
            dict(
                id=2,
                name="admin",
                title="Administrators",
                description=None
            ),
            dict(
                id=3,
                name="poweruser",
                title="Power User",
                description=None
            )
        ]
    )



def downgrade():
    pass
