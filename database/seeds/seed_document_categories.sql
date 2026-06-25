-- HCI AI — Document Categories Reference Seed
-- Canonical category list used in documents.document_category
-- Inserted into a reference table for validation and UI population.

CREATE TABLE IF NOT EXISTS document_categories (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    category    TEXT UNIQUE NOT NULL,
    label       TEXT NOT NULL,
    description TEXT,
    sort_order  INTEGER,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO document_categories (category, label, description, sort_order) VALUES
    ('drawings',                'Drawings',                 'Architectural, structural, MEP drawings',              1),
    ('specifications',          'Specifications',           'Project specifications, scope of work documents',      2),
    ('bids',                    'Bids',                     'Bid proposals, quotes, bid leveling sheets',           3),
    ('contracts',               'Contracts',                'Subcontracts, owner contracts, amendments',            4),
    ('procurement',             'Procurement',              'Purchase orders, submittals, material orders',         5),
    ('submittals',              'Submittals',               'Shop drawings, product data, samples',                 6),
    ('rfis',                    'RFIs',                     'Requests for Information',                             7),
    ('change_orders',           'Change Orders',            'Owner COs, subcontractor change orders',               8),
    ('budgets',                 'Budgets',                  'Budget worksheets, cost reports, GMP summaries',       9),
    ('schedules',               'Schedules',                'Project schedules, look-ahead, baseline schedules',    10),
    ('meeting_minutes',         'Meeting Minutes',          'Owner, subcontractor, and internal meeting notes',     11),
    ('daily_reports',           'Daily Reports',            'Field daily logs, weather logs, crew reports',         12),
    ('photos',                  'Photos',                   'Progress photos, punch list photos, documentation',    13),
    ('client_correspondence',   'Client Correspondence',    'Emails, letters, owner communications',                14),
    ('vendor_correspondence',   'Vendor Correspondence',    'Sub/supplier emails, bid invitations, follow-ups',     15),
    ('sop',                     'SOPs',                     'Standard operating procedures, checklists',            16),
    ('template',                'Templates',                'Blank templates, form documents',                      17),
    ('registry',                'Registry',                 'Vendor registry, contact list, cost code registry',    18),
    ('historical_project',      'Historical Project',       'Completed project records, final cost data',           19),
    ('ai_artifact',             'AI Artifact',              'AI-generated summaries, reports, leveling outputs',    20),
    ('unknown',                 'Unknown',                  'Unclassified or pending classification',               99)
ON CONFLICT (category) DO NOTHING;
