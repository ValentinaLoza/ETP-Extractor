PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS publications (
    id INTEGER PRIMARY KEY,
    part_number TEXT NOT NULL,
    title TEXT,
    revision TEXT,
    revision_date TEXT,
    language TEXT,
    UNIQUE(part_number, revision, language)
);

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY,
    publication_id INTEGER NOT NULL,
    ata TEXT,
    document_key TEXT,
    title TEXT,
    source_path TEXT,
    FOREIGN KEY(publication_id) REFERENCES publications(id)
);

CREATE TABLE IF NOT EXISTS parts (
    id INTEGER PRIMARY KEY,
    part_number TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS ipc_items (
    id INTEGER PRIMARY KEY,
    document_id INTEGER NOT NULL,
    figure TEXT,
    item_number TEXT,
    part_id INTEGER,
    quantity TEXT,
    effectivity TEXT,
    source_reference TEXT,
    FOREIGN KEY(document_id) REFERENCES documents(id),
    FOREIGN KEY(part_id) REFERENCES parts(id)
);

CREATE TABLE IF NOT EXISTS consumables (
    id INTEGER PRIMARY KEY,
    part_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    material TEXT,
    specification TEXT,
    dimensions TEXT,
    validation_status TEXT DEFAULT 'PENDING',
    FOREIGN KEY(part_id) REFERENCES parts(id)
);

CREATE TABLE IF NOT EXISTS alternates (
    id INTEGER PRIMARY KEY,
    source_part_id INTEGER NOT NULL,
    alternate_part_id INTEGER NOT NULL,
    approval_reference TEXT,
    status TEXT DEFAULT 'PENDING',
    FOREIGN KEY(source_part_id) REFERENCES parts(id),
    FOREIGN KEY(alternate_part_id) REFERENCES parts(id)
);
