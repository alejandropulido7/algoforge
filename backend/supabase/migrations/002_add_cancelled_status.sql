-- ==============================================================================
-- Migration 002: Add 'cancelled' status to jobs_status_check constraint
-- ==============================================================================

-- Drop the old constraint if it exists
ALTER TABLE public.jobs
    DROP CONSTRAINT IF EXISTS jobs_status_check;

-- Add updated constraint including 'cancelled'
ALTER TABLE public.jobs
    ADD CONSTRAINT jobs_status_check
    CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled'));
