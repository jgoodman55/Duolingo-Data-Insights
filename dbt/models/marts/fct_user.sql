WITH 

user_stats as (

    SELECT 
    
        fct_user_learning_language.user_id, 

        MIN(fct_user_learning_language.first_activity_ts) AS first_activity_ts,
        MAX(fct_user_learning_language.last_activity_ts) AS last_activity_ts,

        SUM(fct_user_learning_language.total_practices) AS total_practices,

        COUNT(DISTINCT fct_user_learning_language.learning_language) AS cnt_learning_languages,

        CASE 
            WHEN SUM(fct_user_learning_language.user_history_seen) > 0
            THEN CAST(SUM(fct_user_learning_language.user_history_correct) AS FLOAT64)/SUM(fct_user_learning_language.user_history_seen)
            ELSE NULL
        END AS overall_accuracy

    FROM {{ ref('fct_user_learning_language') }} fct_user_learning_language
    GROUP BY fct_user_learning_language.user_id

)

SELECT * FROM user_stats

