-- ==========================================
-- AlgoForge Database Schema & Security
-- ==========================================

-- Jobs table
CREATE TABLE IF NOT EXISTS public.jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    config JSONB NOT NULL DEFAULT '{}'::jsonb,
    progress INTEGER NOT NULL DEFAULT 0,
    current_phase TEXT NOT NULL DEFAULT 'queued',
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

-- Strategies table
CREATE TABLE IF NOT EXISTS public.strategies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES public.jobs(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    rank INTEGER NOT NULL DEFAULT 1,
    total_score FLOAT NOT NULL DEFAULT 0.0,
    sharpe_ratio FLOAT NOT NULL DEFAULT 0.0,
    total_return_pct FLOAT NOT NULL DEFAULT 0.0,
    max_drawdown_pct FLOAT NOT NULL DEFAULT 0.0,
    win_rate FLOAT NOT NULL DEFAULT 0.0,
    profit_factor FLOAT NOT NULL DEFAULT 0.0,
    n_trades INTEGER NOT NULL DEFAULT 0,
    mc_robustness FLOAT NOT NULL DEFAULT 0.0,
    mc_prob_ruin FLOAT NOT NULL DEFAULT 0.0,
    mc_95_drawdown FLOAT NOT NULL DEFAULT 0.0,
    strategy_tree TEXT,
    indicator_config JSONB DEFAULT '{}'::jsonb,
    entry_rules JSONB DEFAULT '{}'::jsonb,
    exit_rules JSONB DEFAULT '{}'::jsonb,
    equity_curve FLOAT[] DEFAULT ARRAY[]::FLOAT[],
    trade_log JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for high-performance querying
CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON public.jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON public.jobs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_strategies_job_id ON public.strategies(job_id);
CREATE INDEX IF NOT EXISTS idx_strategies_rank ON public.strategies(job_id, rank ASC);
CREATE INDEX IF NOT EXISTS idx_strategies_score ON public.strategies(job_id, total_score DESC);

-- Enable Row Level Security (RLS)
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.strategies ENABLE ROW LEVEL SECURITY;

-- RLS Policies
DROP POLICY IF EXISTS "Users can manage their own jobs" ON public.jobs;
CREATE POLICY "Users can manage their own jobs" ON public.jobs
    FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can view their own strategies" ON public.strategies;
CREATE POLICY "Users can view their own strategies" ON public.strategies
    FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Enable Realtime for job updates
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_publication_tables 
        WHERE pubname = 'supabase_realtime' 
        AND schemaname = 'public' 
        AND tablename = 'jobs'
    ) THEN
        ALTER PUBLICATION supabase_realtime ADD TABLE public.jobs;
    END IF;
END $$;
