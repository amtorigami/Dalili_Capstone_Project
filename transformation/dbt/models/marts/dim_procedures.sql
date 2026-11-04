{{ config(materialized='table') }}

select
    -- Clé primaire dbt pour l'historique SCD2
    dbt_scd_id as dim_procedure_key,
    procedure_id,
    nom_procedure,
    ministere,
    cout_mad,      -- Ajouté pour corriger l'erreur
    delai_jours,   -- Ajouté par sécurité
    url_officielle,
    -- Métadonnées temporelles SCD2
    dbt_valid_from,
    dbt_valid_to,
    case when dbt_valid_to is null then true else false end as is_current
from {{ ref('snp_procedures') }}
