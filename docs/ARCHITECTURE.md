# SkillSphere AI — Architecture & Data Warehouse Specification

## 1. Dimensional Star Schema Architecture

SkillSphere AI implements a clean star schema tailored for high-performance job market analytics and multidimensional OLAP slicing.

```
                  +-------------------+
                  |      DimDate      |
                  +-------------------+
                  | date_key (PK)     |
                  | full_date         |
                  | year, month, day  |
                  +---------+---------+
                            | 1
                            |
                            | N
+------------------+      +-+------------------+      +--------------------+
|      DimJob      |      |    FactJobSkill    |      |      DimSkill      |
+------------------+      +--------------------+      +--------------------+
| job_key (PK)     | 1  N | job_skill_fact_key | N  1 | skill_key (PK)     |
| source_job_id    +------+ job_key (FK)       +------+ canonical_name      |
| job_title        |      | skill_key (FK)     |      | skill_category     |
| job_category     |      | company_key (FK)   |      | taxonomy_version   |
| min_max_salary   |      | location_key (FK)  |      +--------------------+
+------------------+      | date_key (FK)      |
                          | mention_count      |
                          | is_required        |
                          | skill_weight       |
                          +---------+----------+
                                    | N
                                    |
                                    | 1
                          +---------+----------+
                          |    DimLocation     |
                          +--------------------+
                          | location_key (PK)  |
                          | city, state        |
                          | country, region    |
                          +--------------------+
```

## 2. Fact Grain & Measures
- **Fact Table**: `FactJobSkill`
- **Grain**: One row per distinct canonical skill mention per job posting.
- **Additive Measures**:
  - `mention_count`: Count of occurrences (1)
  - `PostingCountContribution`: Distinct job posting contribution (1)
- **Semi-Additive Measures**:
  - `skill_weight`: 2.0 for required skills, 1.0 for preferred skills.
  - `min_salary` & `max_salary`: Numerical compensation metrics.

## 3. Data Mining & ML Pipelines
1. **Classification**:
   - Algorithms: Decision Tree & Multinomial Naive Bayes.
   - Objective: Predict `job_category` from text descriptions & skills.
   - Split: 75% Train / 25% Test with TF-IDF vectorization.
2. **Clustering**:
   - Algorithm: K-Means (K=2 to 8).
   - Objective: Identify implicit job requirement sub-clusters.
   - Dimension Reduction: 2D PCA representation for UI scatter plot.
3. **Association Mining**:
   - Algorithm: Apriori algorithm via `mlxtend`.
   - Objective: Mine frequent skill combinations and derive Support, Confidence, Lift.
