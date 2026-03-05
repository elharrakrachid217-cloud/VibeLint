-- Harden RLS on ALL public tables before the repo goes public.
-- Ensures the anon key can only INSERT (+ UPDATE for mcp_installs upsert).
-- Nobody can SELECT, DELETE, or otherwise read data with just the anon key.
--
-- Run in Supabase: SQL Editor → New query → paste and run

-- ── 1. Drop every existing policy on all three tables ──
DO $$
DECLARE
  pol RECORD;
BEGIN
  FOR pol IN
    SELECT policyname, tablename
      FROM pg_policies
     WHERE schemaname = 'public'
       AND tablename IN ('mcp_installs', 'waitlist_emails', 'support_requests')
  LOOP
    EXECUTE format('DROP POLICY %I ON public.%I', pol.policyname, pol.tablename);
  END LOOP;
END
$$;

-- ── 2. Enable RLS on all tables ──
ALTER TABLE public.mcp_installs     ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.waitlist_emails   ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.support_requests  ENABLE ROW LEVEL SECURITY;

-- ── 3. Revoke everything from anon, then grant only what's needed ──
REVOKE ALL ON public.mcp_installs     FROM anon;
REVOKE ALL ON public.waitlist_emails   FROM anon;
REVOKE ALL ON public.support_requests  FROM anon;

-- mcp_installs: INSERT + UPDATE (needed for PostgREST upsert via Prefer: resolution=merge-duplicates)
GRANT INSERT, UPDATE ON public.mcp_installs TO anon;

-- waitlist_emails: INSERT only
GRANT INSERT ON public.waitlist_emails TO anon;

-- support_requests: INSERT only
GRANT INSERT ON public.support_requests TO anon;

-- ── 4. Create tight RLS policies ──

-- mcp_installs — allow insert and upsert (update existing row on conflict)
CREATE POLICY "anon_insert" ON public.mcp_installs
  FOR INSERT WITH CHECK (true);

CREATE POLICY "anon_update" ON public.mcp_installs
  FOR UPDATE USING (true) WITH CHECK (true);

-- waitlist_emails — insert only, no read
CREATE POLICY "anon_insert" ON public.waitlist_emails
  FOR INSERT WITH CHECK (true);

-- support_requests — insert only, no read
CREATE POLICY "anon_insert" ON public.support_requests
  FOR INSERT WITH CHECK (true);

-- ── 5. Reload PostgREST schema cache ──
NOTIFY pgrst, 'reload schema';
