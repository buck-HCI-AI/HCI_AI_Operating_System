-- HCI AI — CSI MasterFormat 16-Division Seed Data
-- Run after 003_registry_schema.sql

INSERT INTO csi_divisions (division_code, division_name, description) VALUES
    ('01', 'General Requirements',          'Project management, temporary facilities, closeout'),
    ('02', 'Site Construction',             'Demolition, earthwork, site utilities, landscaping'),
    ('03', 'Concrete',                      'Cast-in-place, precast, shotcrete, concrete repairs'),
    ('04', 'Masonry',                       'Unit masonry, stone, masonry restoration'),
    ('05', 'Metals',                        'Structural steel, metal fabrications, ornamental metal'),
    ('06', 'Wood & Plastics',               'Rough carpentry, finish carpentry, millwork, cabinetry'),
    ('07', 'Thermal & Moisture Protection', 'Waterproofing, insulation, air barrier, roofing, siding'),
    ('08', 'Doors & Windows',               'Doors, frames, hardware, windows, glazing, storefronts'),
    ('09', 'Finishes',                      'Drywall, tile, flooring, painting, wall coverings'),
    ('10', 'Specialties',                   'Toilet accessories, fire protection specialties, signage'),
    ('11', 'Equipment',                     'Appliances, residential equipment'),
    ('12', 'Furnishings',                   'Window treatments, furniture, casework'),
    ('13', 'Special Construction',          'Saunas, pools, spas, wine rooms'),
    ('14', 'Conveying Systems',             'Elevators, lifts, dumbwaiters'),
    ('15', 'Mechanical',                    'Plumbing, HVAC, fire suppression, radiant, snowmelt'),
    ('16', 'Electrical',                    'Power, lighting, data/comm, AV, security, controls')
ON CONFLICT (division_code) DO NOTHING;
