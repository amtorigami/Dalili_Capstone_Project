{{ config(materialized='table') }}

with unnested_docs as (
    select distinct
        doc as document_name
    from {{ ref('stg_procedures') }},
    unnest(pieces_requises) as doc
)

select
    md5(document_name) as dim_document_key,
    document_name
from unnested_docs
