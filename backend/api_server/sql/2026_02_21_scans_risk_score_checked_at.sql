BEGIN;

ALTER TABLE public.scans
    ADD COLUMN IF NOT EXISTS risk_score INTEGER;

UPDATE public.scans
SET risk_score = final_score
WHERE risk_score IS NULL
  AND final_score IS NOT NULL;

ALTER TABLE public.scans
    ADD COLUMN IF NOT EXISTS checked_at TIMESTAMPTZ;

UPDATE public.scans
SET checked_at = COALESCE(created_at, NOW())
WHERE checked_at IS NULL;

ALTER TABLE public.scans
    ALTER COLUMN checked_at SET DEFAULT NOW();

ALTER TABLE public.scans
    ALTER COLUMN checked_at SET NOT NULL;

ALTER TABLE public.scans
    DROP COLUMN IF EXISTS final_score;

ALTER TABLE public.scans
    DROP COLUMN IF EXISTS created_at;

COMMIT;
