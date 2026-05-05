select
    id as location_id,
    name as location_name,
    tax_rate,
    cast(opened_at as date) as opened_date
from {{ source(env_var('_DBT_DB_NAME'), 'raw_stores') }}
