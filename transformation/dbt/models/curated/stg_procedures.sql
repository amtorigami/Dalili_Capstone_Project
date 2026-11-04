{{ config(materialized='view') }}

with raw_json_data as (
    select * from read_json_auto('/home/atm/atm2526/bootc/Capstone_Project/collect/mock_api/*.json')
)

select
    md5(concat(procedure_id, '_', cast(current_date as varchar))) as stg_id,
    procedure_id,
    nom_procedure,
    ministere,
    cast(cout_mad as bigint) as cout_mad,
    cast(delai_jours as bigint) as delai_jours,
    url_officielle,
    pieces_requises,
    current_timestamp as extraction_at
from raw_json_data
