{{ config(materialized='table') }}

select
    md5(concat(stg.procedure_id, '_', cast(stg.extraction_at as string))) as fact_key,
    dim_p.dim_procedure_key,
    md5(stg.ministere) as dim_administration_key,
    stg.cout_mad,
    stg.delai_jours,
    stg.extraction_at as metrics_date
from {{ ref('stg_procedures') }} stg
left join {{ ref('dim_procedures') }} dim_p 
    on stg.procedure_id = dim_p.procedure_id 
    and dim_p.is_current = true
