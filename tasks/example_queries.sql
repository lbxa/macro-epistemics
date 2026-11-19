-- Economic categories, ordered by the published May Claude usage percentage.
SELECT code,name,usage_pct,indexed_task_count,coverage_note
FROM category_coverage ORDER BY usage_pct DESC;

-- Source-ready financial inputs that have not been flagged for reference review.
SELECT task_id,title,reference_type,oracle_verification
FROM source_ready_candidates WHERE benchmark_id='finqa' LIMIT 20;

-- All sources mapped to an occupational category.
SELECT b.name,b.grading,b.prerequisites,b.dataset_url
FROM benchmarks b JOIN benchmark_categories c USING(benchmark_id)
WHERE c.category_code='23';

-- Known category coverage gaps.
SELECT code,name,proposed_task_families,coverage_note
FROM categories WHERE code IN (SELECT code FROM category_coverage WHERE indexed_task_count=0);

-- Inputs that require an additional runtime or source snapshot.
SELECT benchmark_id,input_status,count(*) AS records
FROM tasks WHERE input_status<>'self_contained'
GROUP BY benchmark_id,input_status;

-- Source-group counts for clustering and train/test splits.
SELECT benchmark_id,count(DISTINCT group_id) AS source_groups,count(*) AS task_records
FROM tasks GROUP BY benchmark_id;

-- Look for repeated input text before selecting experimental cases.
SELECT benchmark_id,content_sha256,count(*) AS records
FROM tasks WHERE prompt IS NOT NULL
GROUP BY benchmark_id,content_sha256 HAVING count(*)>1;

-- Keep the two confidence targets separate after future experiments.
SELECT stage,avg(p_claim_true),avg(p_jury_upholds),count(*) AS observations
FROM observations GROUP BY stage;
