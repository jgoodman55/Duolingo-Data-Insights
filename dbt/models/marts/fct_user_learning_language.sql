WITH

lexeme_accuracy AS (

    SELECT 

        stg_duolingo.user_id, 
        cd_language.language_desc as learning_language,
        stg_duolingo.lexeme_id, 

        MIN(stg_duolingo.event_ts) as first_activity_ts,
        MAX(stg_duolingo.event_ts) as last_activity_ts,

        MAX(stg_duolingo.history_correct) AS lexeme_history_correct, 
        MAX(stg_duolingo.history_seen) AS lexeme_history_seen

    FROM {{ ref('stg_duolingo') }} stg_duolingo
    LEFT JOIN {{ ref('cd_language') }} cd_language on stg_duolingo.learning_language = cd_language.language_cd
    GROUP BY stg_duolingo.user_id, 2, stg_duolingo.lexeme_id

),

user_learning_language_accuracy AS (
  
    SELECT 
    
        user_id, 
        learning_language,

        MIN(first_activity_ts) AS first_activity_ts,
        MAX(last_activity_ts) AS last_activity_ts,
        
        SUM(lexeme_history_correct) AS user_history_correct, 
        SUM(lexeme_history_seen) AS user_history_seen
    
    FROM  lexeme_accuracy
    GROUP BY user_id, learning_language

),

user_learning_language_stats AS (

    SELECT 
    
        user_learning_language_accuracy.user_id, 
        user_learning_language_accuracy.learning_language,

        MAX(user_learning_language_accuracy.user_history_correct) AS user_history_correct,
        MAX(user_learning_language_accuracy.user_history_seen) AS user_history_seen,


        CASE 
            WHEN MAX(user_learning_language_accuracy.user_history_seen) > 0
            THEN CAST(MAX(user_learning_language_accuracy.user_history_correct) AS FLOAT64)/MAX(user_learning_language_accuracy.user_history_seen)
            ELSE NULL
        END AS overall_accuracy,

        MIN(user_learning_language_accuracy.first_activity_ts) AS first_activity_ts,
        MAX(user_learning_language_accuracy.last_activity_ts) AS last_activity_ts,

        COUNT(*) AS total_practices

    FROM user_learning_language_accuracy
    GROUP BY user_learning_language_accuracy.user_id, user_learning_language_accuracy.learning_language

)

SELECT * FROM user_learning_language_stats