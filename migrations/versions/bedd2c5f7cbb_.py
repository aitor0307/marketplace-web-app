"""listing search: pg_trgm/unaccent + trigram index on title, tags and body

Revision ID: bedd2c5f7cbb
Revises: 1363240a458f
Create Date: 2026-10-11 13:06:48.255999

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bedd2c5f7cbb'
down_revision = '1363240a458f'
branch_labels = None
depends_on = None


def upgrade():
    # Extensions + the functions the index is built on: autogenerate can't
    # see these. Frozen copy of SEARCH_DDL in app/models/listing.py.
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent")
    op.execute("""
    DO $do$
    DECLARE unaccent_schema text;
    BEGIN
        SELECT n.nspname INTO unaccent_schema
        FROM pg_extension e JOIN pg_namespace n ON n.oid = e.extnamespace
        WHERE e.extname = 'unaccent';

        EXECUTE
            'CREATE OR REPLACE FUNCTION public.search_normalize(value text) '
            'RETURNS text LANGUAGE sql IMMUTABLE PARALLEL SAFE STRICT '
            'AS $body$ SELECT ' || quote_ident(unaccent_schema) || '.unaccent('
            || quote_literal(unaccent_schema || '.unaccent') || '::regdictionary, lower(value)) $body$';
    END
    $do$
    """)
    op.execute("""
    CREATE OR REPLACE FUNCTION public.listing_search_document(title text, body text, data jsonb)
    RETURNS text LANGUAGE sql IMMUTABLE PARALLEL SAFE
    AS $$ SELECT public.search_normalize(concat_ws(' ', title, data ->> 'tags', body)) $$
    """)

    # Autogenerate drops the operator class from this expression index; it
    # has to be spelled out in the expression itself.
    op.create_index(
        'ix_listing_search_document_trgm',
        'listing',
        [sa.text('listing_search_document(title, body, external_data) gin_trgm_ops')],
        unique=False,
        postgresql_using='gin',
    )


def downgrade():
    op.drop_index('ix_listing_search_document_trgm', table_name='listing')
    op.execute("DROP FUNCTION IF EXISTS public.listing_search_document(text, text, jsonb)")
    op.execute("DROP FUNCTION IF EXISTS public.search_normalize(text)")
    # The extensions are left installed: other objects may come to rely on them.
