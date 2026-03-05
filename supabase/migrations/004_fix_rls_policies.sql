-- Fix RLS + table grants for waitlist_emails and support_requests.
-- Run this in your Supabase project: SQL Editor → New query → paste and run

-- ── Step 1: nuke every existing policy on both tables ──
DO $$
DECLARE
  pol RECORD;
BEGIN
  FOR pol IN
    SELECT policyname, tablename
      FROM pg_policies
     WHERE schemaname = 'public'
       AND tablename IN ('waitlist_emails', 'support_requests')
  LOOP
    EXECUTE format('DROP POLICY %I ON public.%I', pol.policyname, pol.tablename);
  END LOOP;
END
$$;

-- ── Step 2: enable RLS ──
ALTER TABLE public.waitlist_emails  ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.support_requests ENABLE ROW LEVEL SECURITY;

-- ── Step 3: grant table-level INSERT to the anon role ──
-- Without this, RLS policies alone won't help — the role can't touch the table.
GRANT INSERT ON public.waitlist_emails  TO anon;
GRANT INSERT ON public.support_requests TO anon;

-- ── Step 4: INSERT-only RLS policy, open to all roles ──
CREATE POLICY "insert_only" ON public.waitlist_emails
  FOR INSERT
  WITH CHECK (true);

CREATE POLICY "insert_only" ON public.support_requests
  FOR INSERT
  WITH CHECK (true);

-- ── Step 5: reload PostgREST schema cache ──
NOTIFY pgrst, 'reload schema';
