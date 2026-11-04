{% snapshot snp_procedures %}

{{
    config(
      target_schema='main',
      unique_key='procedure_id',
      strategy='check',
      check_cols=['cout_mad', 'delai_jours', 'nom_procedure'],
    )
}}

select
    procedure_id,
    nom_procedure,
    ministere,
    cout_mad,
    delai_jours,
    url_officielle
from {{ ref('stg_procedures') }}

{% endsnapshot %}
