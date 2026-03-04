-- Support form submissions from the VibeLint landing page
-- Run this in your Supabase project: SQL Editor → New query → paste and run

CREATE TABLE support_requests (
  id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  full_name   TEXT NOT NULL,
  email       TEXT NOT NULL,
  message     TEXT NOT NULL,
  created_at  TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE support_requests ENABLE ROW LEVEL SECURITY;

-- Allow anonymous inserts from the landing page (anon key)
CREATE POLICY "allow_anon_insert" ON support_requests
  FOR INSERT
  TO anon
  WITH CHECK (true);
