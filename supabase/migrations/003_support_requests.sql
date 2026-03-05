-- Support form submissions from the VibeLint landing page
-- Run this in your Supabase project: SQL Editor → New query → paste and run

CREATE TABLE support_requests (
  id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  full_name   TEXT NOT NULL,
  email       TEXT NOT NULL,
  message     TEXT NOT NULL,
  created_at  TIMESTAMPTZ DEFAULT now()
);

-- RLS disabled: simple collection table, anon inserts only
ALTER TABLE support_requests DISABLE ROW LEVEL SECURITY;
