{{ config(materialized='view') }}

/* 
QUESTION METIER : 
Quels sont les documents exacts requis pour chaque démarche, 
et quels sont les frais associés à préparer par le citoyen ?
*/

select 
    p.nom_procedure,
    p.ministere,
    p.cout_mad as frais_en_mad,
    doc.document_name as piece_a_fournir,
    p.url_officielle
from {{ ref('fct_procedures') }} f
join {{ ref('dim_procedures') }} p on f.dim_procedure_key = p.dim_procedure_key
join {{ ref('stg_procedures') }} stg on p.procedure_id = stg.procedure_id
join {{ ref('dim_documents') }} doc on list_contains(stg.pieces_requises, doc.document_name)
where p.is_current = true
