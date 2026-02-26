WITH 

user_stats as (

    SELECT 
    
        dim_user_learning_language.user_id, 

        MIN(dim_user_learning_language.first_activity_ts) AS first_activity_ts,
        MAX(dim_user_learning_language.last_activity_ts) AS last_activity_ts,

        SUM(dim_user_learning_language.total_practices) AS total_practices,

        COUNT(DISTINCT dim_user_learning_language.learning_language) AS cnt_learning_languages,

        CASE 
            WHEN SUM(dim_user_learning_language.user_history_seen) > 0
            THEN CAST(SUM(dim_user_learning_language.user_history_correct) AS FLOAT64)/SUM(dim_user_learning_language.user_history_seen)
            ELSE NULL
        END AS overall_accuracy

    FROM {{ ref('dim_user_learning_language') }} dim_user_learning_language
    GROUP BY dim_user_learning_language.user_id

)

SELECT * FROM user_stats

