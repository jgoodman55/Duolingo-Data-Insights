WITH

daily_language_activity as (

SELECT

    stg_duolingo.event_dt,
    cd_language.language_desc as learning_language,

    count(1) as practices_completed,
    count(distinct user_id) as active_users,
    count(distinct lexeme_id) as unique_lexeme_practiced,

FROM {{ ref('stg_duolingo') }} stg_duolingo
LEFT JOIN {{ ref('cd_language') }} cd_language on stg_duolingo.learning_language = cd_language.language_cd

GROUP BY
    stg_duolingo.event_dt,
    2
)

select * from daily_language_activity