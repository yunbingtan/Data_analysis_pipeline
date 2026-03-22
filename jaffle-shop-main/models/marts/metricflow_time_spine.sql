-- metricflow_time_spine.sql
with recursive
calendar as (
    select date('2000-01-01') as date_day
    union all
    select date(date_day, '+1 day')
    from calendar
    where date_day < date('2030-12-31')
)

select date_day
from calendar
