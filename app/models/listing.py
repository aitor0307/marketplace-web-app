from sqlalchemy import DDL, Index, column, event, func

from app.extensions import db
from app.models.mixins import CRUDMixin

# --- Search ---------------------------------------------------------------------
# Listings are searched by trigram similarity (pg_trgm) over one normalised
# document: lower-cased, accent-free title + tags + description. Two SQL
# functions build it so the GIN index below and the queries in listings_ops
# share the exact same expression:
#   search_normalize(text)                    -> unaccent(lower(text))
#   listing_search_document(title, body, data) -> search_normalize(title tags body)
# Both are IMMUTABLE so they can back an index. search_normalize schema-qualifies
# unaccent with whatever schema the extension lives in (public locally, but
# "extensions" on Supabase).
#
# db.create_all() (the test suite) gets these from the before_create hook at
# the bottom; real databases need the same SEARCH_DDL statements in the
# migration that creates the index, since autogenerate can't see them.
SEARCH_DDL = (
    "CREATE EXTENSION IF NOT EXISTS pg_trgm",
    "CREATE EXTENSION IF NOT EXISTS unaccent",
    """
    DO $do$
    DECLARE unaccent_schema text;
    BEGIN
        SELECT n.nspname INTO unaccent_schema
        FROM pg_extension e JOIN pg_namespace n ON n.oid = e.extnamespace
        WHERE e.extname = 'unaccent';

        -- Concatenation rather than format(): DDL() would treat its percent placeholders as its own.
        EXECUTE
            'CREATE OR REPLACE FUNCTION public.search_normalize(value text) '
            'RETURNS text LANGUAGE sql IMMUTABLE PARALLEL SAFE STRICT '
            'AS $body$ SELECT ' || quote_ident(unaccent_schema) || '.unaccent('
            || quote_literal(unaccent_schema || '.unaccent') || '::regdictionary, lower(value)) $body$';
    END
    $do$
    """,
    """
    CREATE OR REPLACE FUNCTION public.listing_search_document(title text, body text, data jsonb)
    RETURNS text LANGUAGE sql IMMUTABLE PARALLEL SAFE
    AS $$ SELECT public.search_normalize(concat_ws(' ', title, data ->> 'tags', body)) $$
    """,
)


def listing_search_document(title, body, external_data):
    return func.listing_search_document(title, body, external_data)


class Listing(CRUDMixin, db.Model):
    __tablename__ = "listing"
    __table_args__ = (
        Index(
            "ix_listing_search_document_trgm",
            listing_search_document(column("title"), column("body"), column("external_data")).label(
                "search_document"
            ),
            postgresql_using="gin",
            postgresql_ops={"search_document": "gin_trgm_ops"},
        ),
    )

    title = db.Column(db.String(100))
    price = db.Column(db.Float)
    condition = db.Column(db.String(10))
    body = db.Column(db.String(300))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    @classmethod
    def search_document(cls):
        return listing_search_document(cls.title, cls.body, cls.external_data)


for statement in SEARCH_DDL:
    event.listen(
        Listing.__table__, "before_create", DDL(statement).execute_if(dialect="postgresql")
    )
