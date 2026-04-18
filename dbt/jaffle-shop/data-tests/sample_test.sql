SELECT * 
FROM {{ ref('customers') }} 
WHERE customer_id IS NULL
