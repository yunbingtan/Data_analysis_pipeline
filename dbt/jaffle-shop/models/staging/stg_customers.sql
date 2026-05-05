with

source as (

    select * from {{ source(env_var('_DBT_DB_NAME'), 'raw_customers') }}

),

renamed as (

    select

        ----------  ids
        id as customer_id,

        ---------- text
        name as customer_name

    from source

)

select * from renamed
