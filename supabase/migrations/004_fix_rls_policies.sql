-- Fix RLS policies for waitlist_emails and support_requests tables.
-- The tables exist but anon inserts are blocked.
-- Run this in your Supabase project: SQL Editor → New query → paste and run

-- Drop existing policies (safe even if they don't exist)
DROP POLICY IF EXISTS "allow_anon_insert" ON waitlist_emails;
DROP POLICY IF EXISTS "allow_anon_insert" ON support_requests;

-- Re-create INSERT policies explicitly for the anon role
CREATE POLICY "allow_anon_insert" ON waitlist_emails
  FOR INSERT
  TO anon
  WITH CHECK (true);

CREATE POLICY "allow_anon_insert" ON support_requests
  FOR INSERT
  TO anon
  WITH CHECK (true);

-- Add SELECT policy so the dashboard (authenticated/service role) can read rows
CREATE POLICY "allow_service_select" ON waitlist_emails
  FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "allow_service_select" ON support_requests
  FOR SELECT
  TO authenticated
  USING (true);
