-- VibeLint MCP unique install tracking
-- Run this in your Supabase project: SQL Editor → New query → paste and run

CREATE TABLE mcp_installs (
  machine_id  TEXT PRIMARY KEY,
  os          TEXT,
  platform    TEXT,
  version     TEXT DEFAULT '1.0.0',
  first_seen  TIMESTAMPTZ DEFAULT now(),
  last_seen   TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE mcp_installs ENABLE ROW LEVEL SECURITY;

-- Allow anonymous inserts/upserts from the anon key
CREATE POLICY "allow_anon_upsert" ON mcp_installs
  FOR ALL USING (true) WITH CHECK (true);
