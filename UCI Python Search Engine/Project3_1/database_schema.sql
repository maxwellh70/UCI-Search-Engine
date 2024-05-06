create table public.inverted_index
(
    token           character varying(200) primary key not null,
    doc_ids         character varying[],
    frequency_array integer[],
    tfidf_array     double precision[],
    tags_array      jsonb 
);
