"""Database schema definition for R2C2 Voice Coach."""

import sqlite3
from pathlib import Path
from typing import Optional


def get_schema_sql() -> str:
    """Return the SQL schema for creating all tables."""
    return """
    -- Sessions table: stores coaching session metadata
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        start_time DATETIME NOT NULL,
        end_time DATETIME,
        feedback_data TEXT,  -- JSON serialized feedback data
        session_summary TEXT,  -- JSON serialized session summary
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Index for querying sessions by user
    CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
    CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON sessions(start_time);
    
    -- Development plans table: stores goals and action items
    CREATE TABLE IF NOT EXISTS development_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        goal_text TEXT NOT NULL,
        goal_type TEXT CHECK(goal_type IN ('start', 'stop', 'continue')),
        specific_behavior TEXT,
        measurable_criteria TEXT,
        target_date DATE,
        action_steps TEXT,  -- JSON array of action steps
        is_completed BOOLEAN DEFAULT FALSE,
        completed_at DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
    );
    
    -- Index for querying development plans by session
    CREATE INDEX IF NOT EXISTS idx_development_plans_session_id ON development_plans(session_id);
    CREATE INDEX IF NOT EXISTS idx_development_plans_completed ON development_plans(is_completed);
    
    -- Emotion events table: stores detected emotions during session
    CREATE TABLE IF NOT EXISTS emotion_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        timestamp DATETIME NOT NULL,
        emotion_type TEXT NOT NULL CHECK(emotion_type IN ('neutral', 'defensive', 'frustrated', 'sad', 'anxious', 'positive')),
        confidence FLOAT CHECK(confidence >= 0.0 AND confidence <= 1.0),
        r2c2_phase TEXT CHECK(r2c2_phase IN ('relationship', 'reaction', 'content', 'coaching')),
        audio_features TEXT,  -- JSON serialized audio features
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
    );
    
    -- Index for querying emotions by session and timestamp
    CREATE INDEX IF NOT EXISTS idx_emotion_events_session_id ON emotion_events(session_id);
    CREATE INDEX IF NOT EXISTS idx_emotion_events_timestamp ON emotion_events(timestamp);
    CREATE INDEX IF NOT EXISTS idx_emotion_events_session_timestamp ON emotion_events(session_id, timestamp);
    
    -- Phase transitions table: tracks R2C2 phase changes
    CREATE TABLE IF NOT EXISTS phase_transitions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        from_phase TEXT NOT NULL CHECK(from_phase IN ('relationship', 'reaction', 'content', 'coaching')),
        to_phase TEXT NOT NULL CHECK(to_phase IN ('relationship', 'reaction', 'content', 'coaching')),
        transition_time DATETIME NOT NULL,
        trigger_reason TEXT,
        time_in_previous_phase FLOAT,  -- seconds
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
    );
    
    -- Index for querying phase transitions by session
    CREATE INDEX IF NOT EXISTS idx_phase_transitions_session_id ON phase_transitions(session_id);
    CREATE INDEX IF NOT EXISTS idx_phase_transitions_time ON phase_transitions(transition_time);
    """


def initialize_database(db_path: Optional[str] = None) -> str:
    """
    Initialize the database with the schema.
    
    Args:
        db_path: Path to the SQLite database file. If None, uses default location.
        
    Returns:
        The path to the initialized database.
    """
    if db_path is None:
        # Default to server/data/r2c2_coach.db
        db_path = str(Path(__file__).parent.parent / "data" / "r2c2_coach.db")
    
    # Create directory if it doesn't exist
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Connect and create schema
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.executescript(get_schema_sql())
        conn.commit()
        print(f"Database initialized successfully at: {db_path}")
    finally:
        conn.close()
    
    return db_path


if __name__ == "__main__":
    # Allow running this script directly to initialize the database
    import sys
    db_path = sys.argv[1] if len(sys.argv) > 1 else None
    initialize_database(db_path)
