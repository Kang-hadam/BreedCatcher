"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
import os

import sqlalchemy as sa
import sqlalchemy_utils
from alembic import op

DB_SCHEMA = os.getenv('DB_SCHEMA', '')
DB_SCHEMA_DOT = DB_SCHEMA + '.' if DB_SCHEMA else ''

${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade():
    ${upgrades.replace(f"schema='{schema}'", 'schema=DB_SCHEMA').replace(f"'ix_{schema}_", "'ix_' + DB_SCHEMA + '_").replace(f", ['{schema}.", ", [DB_SCHEMA_DOT + '") \
     .replace(f"nextval(\"{schema}.\"", "nextval(\"+DB_SCHEMA+\".").replace("PasswordType(length=1137)", "PasswordType(schemes=['pbkdf2_sha512', 'md5_crypt'], deprecated=['md5_crypt'])") if upgrades else "pass"}


def downgrade():
    ${downgrades.replace(f"schema='{schema}'", 'schema=DB_SCHEMA').replace(f"'ix_{schema}_", "'ix_' + DB_SCHEMA + '_").replace(f", ['{schema}.", ", [DB_SCHEMA_DOT + '") \
     .replace(f"nextval('{schema}.", "nextval('\"+DB_SCHEMA_DOT+\"") if downgrades else "pass"}