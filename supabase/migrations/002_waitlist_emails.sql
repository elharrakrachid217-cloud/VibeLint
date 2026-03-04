-- Waitlist email collection for the VibeLint landing page
-- Run this in your Supabase project: SQL Editor → New query → paste and run

CREATE TABLE waitlist_emails (
  id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  email       TEXT NOT NULL UNIQUE,
  source      TEXT DEFAULT 'landing',
  created_at  TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE waitlist_emails ENABLE ROW LEVEL SECURITY;

-- Allow anonymous inserts from the landing page (anon key)
CREATE POLICY "allow_anon_insert" ON waitlist_emails
  FOR INSERT
  TO anon
  WITH CHECK (true);
