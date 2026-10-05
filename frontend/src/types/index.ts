export interface KpiMetrics {
  total_job_postings: number;
  unique_companies: number;
  unique_skills: number;
  job_categories: number;
  latest_dataset_refresh: string;
  etl_quality_score: number;
}

export interface SkillDemandItem {
  skill: string;
  category: string;
  posting_count: number;
  avg_salary: number;
}

export interface JobItem {
  job_key: number;
  source_job_id: string;
  job_title: string;
  job_category: string;
  company_name: string;
  city: string;
  country: string;
  experience_level: string;
  employment_type: string;
  min_salary: number;
  max_salary: number;
  extracted_skills: string[];
  description: string;
  similar_jobs?: Array<{
    job_key: number;
    job_title: string;
    job_category: string;
    similarity_score: number;
  }>;
}

export interface SkillGapAnalysisResult {
  target_role: string;
  experience_level: string;
  coverage_percentage: number;
  confirmed_skill_count: number;
  confirmed_skills_canonical?: string[];
  total_target_skills_analyzed: number;
  matched_skills: Array<{
    skill_name: string;
    category: string;
    demand_count: number;
    demand_percentage: number;
    is_required: boolean;
    priority_score: number;
  }>;
  missing_high_priority: Array<{
    skill_name: string;
    category: string;
    demand_count: number;
    demand_percentage: number;
    is_required: boolean;
    priority_score: number;
  }>;
  missing_secondary: Array<{
    skill_name: string;
    category: string;
    demand_count: number;
    demand_percentage: number;
    is_required: boolean;
    priority_score: number;
  }>;
  roadmap: Array<{
    step: number;
    skill_name: string;
    priority_level: string;
    priority_score: number;
    evidence: string;
    prerequisites: string[];
    related_skills: string[];
  }>;
  suggested_roles: string[];
  methodology: string;
}

export interface OlapQueryResult {
  operation: string;
  explanation: string;
  sql_snippet: string;
  record_count: number;
  data: any[];
}
