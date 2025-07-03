CREATE TABLE law_sections (
    id SERIAL PRIMARY KEY,
    section TEXT,
    title TEXT,
    content TEXT,
    law TEXT,
    punishment TEXT,
    fine TEXT
);

CREATE TABLE law_documents (
    id SERIAL PRIMARY KEY,
    law TEXT,
    filename TEXT,
    content TEXT
);

CREATE TABLE chat_finetune_data (
    id SERIAL PRIMARY KEY,
    prompt TEXT,
    completion TEXT
);
