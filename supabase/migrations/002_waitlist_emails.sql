-- Waitlist email collection for the VibeLint landing page
-- Run this in your Supabase project: SQL Editor → New query → paste and run

CREATE TABLE waitlist_emails (
  id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  email       TEXT NOT NULL UNIQUE,
  source      TEXT DEFAULT 'landing',
  created_at  TIMESTAMPTZ DEFAULT now()
);

-- RLS disabled: simple collection table, anon inserts only
ALTER TABLE waitlist_emails DISABLE ROW LEVEL SECURITY;
