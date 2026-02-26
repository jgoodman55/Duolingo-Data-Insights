WITH

lexeme_accuracy AS (

    SELECT 

        user_id, 
        learning_language,
        lexeme_id, 

        MAX(history_correct) AS lexeme_history_correct, 
        MAX(history_seen) AS lexeme_history_seen

    FROM {{ ref('stg_duolingo') }}
    GROUP BY user_id, learning_language, lexeme_id

),

user_learning_language_accuracy AS (
  
    SELECT 
    
        user_id, 
        learning_language,
        
        SUM(lexeme_history_correct) AS user_history_correct, 
        SUM(lexeme_history_seen) AS user_history_seen
    
    FROM  lexeme_accuracy
    GROUP BY user_id, learning_language

),

user_learning_language_stats AS (

    SELECT 
    
        practice_events_ui_en.user_id, 
        practice_events_ui_en.learning_language,

        MAX(user_learning_language_accuracy.user_history_correct) AS user_history_correct,
        MAX(user_learning_language_accuracy.user_history_seen) AS user_history_seen,


        CASE 
            WHEN MAX(user_learning_language_accuracy.user_history_seen) > 0
            THEN CAST(MAX(user_learning_language_accuracy.user_history_correct) AS FLOAT64)/MAX(user_learning_language_accuracy.user_history_seen)
            ELSE NULL
        END AS overall_accuracy,

        MIN(practice_events_ui_en.event_ts) AS first_activity_ts,
        MAX(practice_events_ui_en.event_ts) AS last_activity_ts,

        COUNT(*) AS total_practices

    FROM user_learning_language_accuracy
    GROUP BY user_learning_language_accuracy.user_id, user_learning_language_accuracy.learning_language

)

SELECT * FROM user_learning_language_stats