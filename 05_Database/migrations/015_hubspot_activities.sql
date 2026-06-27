-- Migration 015: hubspot_activities table
-- Unified activities table for HubSpot connector (CALL, EMAIL, MEETING, NOTE, TASK)
-- The existing hubspot_engagements table predates the connector framework and has
-- a different schema; this table supports the HubSpotConnector.persist() contract.

CREATE TABLE IF NOT EXISTS hubspot_activities (
    id                    SERIAL PRIMARY KEY,
    hubspot_id            TEXT        NOT NULL,
    activity_type         TEXT        NOT NULL,  -- CALL, EMAIL, MEETING, NOTE, TASK
    subject               TEXT,
    body                  TEXT,
    activity_ts           TIMESTAMPTZ,
    duration_ms           INTEGER,
    outcome               TEXT,
    associated_contact_id TEXT,
    associated_deal_id    TEXT,
    associated_company_id TEXT,
    raw_properties        JSONB       NOT NULL DEFAULT '{}',
    synced_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT hubspot_activities_hubspot_id_key UNIQUE (hubspot_id)
);

CREATE INDEX IF NOT EXISTS idx_hubspot_activities_type       ON hubspot_activities (activity_type);
CREATE INDEX IF NOT EXISTS idx_hubspot_activities_contact    ON hubspot_activities (associated_contact_id);
CREATE INDEX IF NOT EXISTS idx_hubspot_activities_deal       ON hubspot_activities (associated_deal_id);
CREATE INDEX IF NOT EXISTS idx_hubspot_activities_ts         ON hubspot_activities (activity_ts DESC);
