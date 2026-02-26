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


        CASE 
            WHEN SUM(user_learning_language_accuracy.user_history_seen) > 0
            THEN CAST(SUM(user_learning_language_accuracy.user_history_correct) AS FLOAT)/SUM(user_learning_language_accuracy.user_history_seen)
            ELSE NULL
        END AS overall_accuracy,

        MIN(practice_events_ui_en.event_ts) AS first_activity_ts,
        MAX(practice_events_ui_en.event_ts) AS last_activity_ts,

        count(*) AS total_practices

    FROM {{ ref('stg_duolingo') }} practice_events_ui_en
    
    LEFT JOIN user_learning_language_accuracy 
        ON practice_events_ui_en.user_id = user_learning_language_accuracy.user_id
        AND practice_events_ui_en.learning_language = user_learning_language_accuracy.learning_language
    
    GROUP BY practice_events_ui_en.user_id, practice_events_ui_en.learning_language

)

SELECT * FROM user_learning_language_stats