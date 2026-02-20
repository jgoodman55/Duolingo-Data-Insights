select

    unique_row_id,
    filename,
    p_recall,
    timestamp,
    delta,
    user_id,
    learning_language,
    ui_language,
    lexeme_id,
    lexeme_string,
    history_seen,
    history_correct,
    session_seen,
    session_correct,
    event_ts,
    event_dt

from {{ source('duolingo', "{{ env_var('GCP_TABLE_NAME') }}") }}