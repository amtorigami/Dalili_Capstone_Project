{{ config(materialized='table') }}

with unique_orgs as (
    select distinct
        ministere as administration_name
    from {{ ref('stg_procedures') }}
)

select
    md5(administration_name) as dim_administration_key,
    administration_name
from unique_orgs
