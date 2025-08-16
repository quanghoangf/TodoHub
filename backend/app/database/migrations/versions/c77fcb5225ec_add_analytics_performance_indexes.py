"""add_analytics_performance_indexes

Revision ID: c77fcb5225ec
Revises: a1b2c3d4e5f6
Create Date: 2025-08-16 18:59:59.478515

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'c77fcb5225ec'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    # Add indexes for habit_logs table to improve analytics query performance
    
    # Index for habit_id and completion_date (used in heatmap and time-based queries)
    op.create_index(
        'idx_habit_logs_habit_completion_date',
        'habit_logs',
        ['habit_id', 'completion_date']
    )
    
    # Index for habit_id and recorded_at (used for chronological analytics)
    op.create_index(
        'idx_habit_logs_habit_recorded_at',
        'habit_logs',
        ['habit_id', 'recorded_at']
    )
    
    # Index for completion_date alone (for cross-habit analytics)
    op.create_index(
        'idx_habit_logs_completion_date',
        'habit_logs',
        ['completion_date']
    )
    
    # Add indexes for habits table to improve dashboard queries
    
    # Index for owner_id and start_date (used in user dashboard)
    op.create_index(
        'idx_habits_owner_start_date',
        'habits',
        ['owner_id', 'start_date']
    )
    
    # Index for owner_id and category (used for category-based analytics)
    op.create_index(
        'idx_habits_owner_category',
        'habits',
        ['owner_id', 'category']
    )
    
    # Add indexes for streak_cache table to improve streak analytics
    
    # Index for habit_id (primary lookup for streak data)
    op.create_index(
        'idx_streak_cache_habit_id',
        'streak_cache',
        ['habit_id']
    )
    
    # Index for current_streak (for finding top streaks)
    op.create_index(
        'idx_streak_cache_current_streak',
        'streak_cache',
        ['current_streak']
    )


def downgrade():
    # Remove indexes in reverse order
    op.drop_index('idx_streak_cache_current_streak')
    op.drop_index('idx_streak_cache_habit_id')
    op.drop_index('idx_habits_owner_category')
    op.drop_index('idx_habits_owner_start_date')
    op.drop_index('idx_habit_logs_completion_date')
    op.drop_index('idx_habit_logs_habit_recorded_at')
    op.drop_index('idx_habit_logs_habit_completion_date')
