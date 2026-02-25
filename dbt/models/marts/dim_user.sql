select
    user_id,
    min(event_ts) as first_activity_ts,
    max(event_ts) as last_activity_ts,
    count(*) as total_events
from {{ ref('stg_duolingo') }}
group by 1