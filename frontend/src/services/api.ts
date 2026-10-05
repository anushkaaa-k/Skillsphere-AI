import { KpiMetrics, SkillDemandItem, JobItem, SkillGapAnalysisResult, OlapQueryResult } from '../types';

const API_BASE = '/api';

export async function fetchKpiMetrics(): Promise<KpiMetrics> {
  const res = await fetch(`${API_BASE}/overview/kpi`);
  return res.json();
}

export async function fetchOverviewCharts(category?: string, city?: string) {
  const params = new URLSearchParams();
  if (category) params.append('category', category);
  if (city) params.append('city', city);
  const res = await fetch(`${API_BASE}/overview/charts?${params.toString()}`);
  return res.json();
}

export async function fetchSkillsDemand(category?: string, city?: string, exp_level?: string): Promise<SkillDemandItem[]> {
  const params = new URLSearchParams();
  if (category) params.append('category', category);
  if (city) params.append('city', city);
  if (exp_level) params.append('exp_level', exp_level);
  const res = await fetch(`${API_BASE}/market/skills-demand?${params.toString()}`);
  return res.json();
}

export async function compareRoles(role_1: string, role_2: string) {
  const res = await fetch(`${API_BASE}/market/compare-roles`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ role_1, role_2 }),
  });
  return res.json();
}

export async function parseResume(formData: FormData) {
  const res = await fetch(`${API_BASE}/resume/parse`, {
    method: 'POST',
    body: formData,
  });
  return res.json();
}

export async function analyzeSkillGap(confirmed_skills: string[], target_role: string, experience_level: string): Promise<SkillGapAnalysisResult> {
  const res = await fetch(`${API_BASE}/skill-gap/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ confirmed_skills, target_role, experience_level }),
  });
  return res.json();
}

export async function fetchUserProfile() {
  const res = await fetch(`${API_BASE}/skill-gap/profile`);
  return res.json();
}

export async function toggleSkillLearned(skill_name: string) {
  const res = await fetch(`${API_BASE}/skill-gap/toggle-skill-learned`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ skill_name }),
  });
  return res.json();
}

export async function searchJobs(query?: string, category?: string, exp_level?: string) {
  const params = new URLSearchParams();
  if (query) params.append('query', query);
  if (category) params.append('category', category);
  if (exp_level) params.append('exp_level', exp_level);
  const res = await fetch(`${API_BASE}/jobs/search?${params.toString()}`);
  return res.json();
}

export async function fetchJobDetail(job_key: number): Promise<JobItem> {
  const res = await fetch(`${API_BASE}/jobs/${job_key}`);
  return res.json();
}

export async function runClassification(algorithm: string) {
  const res = await fetch(`${API_BASE}/mining/classification/train`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ algorithm }),
  });
  return res.json();
}

export async function predictCategory(job_description: string) {
  const res = await fetch(`${API_BASE}/mining/classification/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ job_description }),
  });
  return res.json();
}

export async function runClustering(num_clusters: number) {
  const res = await fetch(`${API_BASE}/mining/clustering/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ num_clusters }),
  });
  return res.json();
}

export async function runApriori(min_support: number, min_confidence: number) {
  const res = await fetch(`${API_BASE}/mining/association/apriori`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ min_support, min_confidence }),
  });
  return res.json();
}

export async function fetchTextMining() {
  const res = await fetch(`${API_BASE}/mining/text-mining/tfidf`);
  return res.json();
}

export async function runOlapQuery(req: any): Promise<OlapQueryResult> {
  const res = await fetch(`${API_BASE}/olap/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  return res.json();
}

export async function fetchEtlLogs() {
  const res = await fetch(`${API_BASE}/etl/logs`);
  return res.json();
}

export async function triggerEtl() {
  const res = await fetch(`${API_BASE}/etl/run`, { method: 'POST' });
  return res.json();
}

export async function fetchSystemSettings() {
  const res = await fetch(`${API_BASE}/settings/info`);
  return res.json();
}

export async function triggerReseed() {
  const res = await fetch(`${API_BASE}/settings/reseed`, { method: 'POST' });
  return res.json();
}
