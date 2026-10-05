import React, { useEffect, useState } from 'react';
import { searchJobs, fetchJobDetail } from '../services/api';
import { JobItem } from '../types';
import { Search, Briefcase, MapPin, Building2, DollarSign, X, Sparkles } from 'lucide-react';

export const JobExplorerPage: React.FC = () => {
  const [jobs, setJobs] = useState<JobItem[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [query, setQuery] = useState<string>('');
  const [category, setCategory] = useState<string>('');
  const [expLevel, setExpLevel] = useState<string>('');
  const [selectedJob, setSelectedJob] = useState<JobItem | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    loadJobs();
  }, [query, category, expLevel]);

  const loadJobs = async () => {
    setLoading(true);
    try {
      const data = await searchJobs(query, category, expLevel);
      setJobs(data.items || []);
      setTotalCount(data.total || 0);
    } catch (err) {
      console.error("Error loading job postings:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectJob = async (job_key: number) => {
    try {
      const detail = await fetchJobDetail(job_key);
      setSelectedJob(detail);
    } catch (err) {
      console.error("Error loading job detail:", err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Search & Filter Bar */}
      <div className="custom-card p-4 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-text-secondary" />
          <input 
            type="text" 
            placeholder="Search job titles, skills, or companies..." 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="input-field pl-9 text-xs w-full"
          />
        </div>

        <div className="flex items-center space-x-3">
          <select 
            value={category} 
            onChange={(e) => setCategory(e.target.value)}
            className="input-field text-xs"
          >
            <option value="">All Categories</option>
            <option value="Data Science & Analytics">Data Science</option>
            <option value="Software Engineering">Software Eng</option>
            <option value="Machine Learning & AI">ML & AI</option>
            <option value="DevOps & Cloud Engineering">DevOps</option>
            <option value="Data Engineering">Data Engineering</option>
            <option value="Cybersecurity">Cybersecurity</option>
          </select>

          <select 
            value={expLevel} 
            onChange={(e) => setExpLevel(e.target.value)}
            className="input-field text-xs"
          >
            <option value="">All Experience Levels</option>
            <option value="Entry Level">Entry Level</option>
            <option value="Mid Level">Mid Level</option>
            <option value="Senior Level">Senior Level</option>
          </select>
        </div>
      </div>

      {/* Postings Counter */}
      <div className="text-xs text-text-secondary font-medium px-1">
        Showing <b>{jobs.length}</b> of <b>{totalCount}</b> verified analytical job postings
      </div>

      {/* Jobs Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {jobs.map((job) => (
          <div 
            key={job.job_key} 
            onClick={() => handleSelectJob(job.job_key)}
            className="custom-card p-4 space-y-3 hover:border-primary cursor-pointer transition shadow-2xs group"
          >
            <div className="flex items-start justify-between">
              <div>
                <h4 className="font-bold text-sm text-text-primary group-hover:text-primary transition">{job.job_title}</h4>
                <p className="text-xs text-text-secondary flex items-center space-x-1 mt-0.5">
                  <Building2 className="w-3 h-3" />
                  <span>{job.company_name}</span>
                </p>
              </div>
              <span className="px-2 py-0.5 bg-surface-mint text-sidebar border border-border rounded text-[10px] font-semibold">
                {job.experience_level}
              </span>
            </div>

            <div className="flex items-center space-x-4 text-xs text-text-secondary">
              <span className="flex items-center space-x-1">
                <MapPin className="w-3 h-3 text-primary" />
                <span>{job.city}, {job.country}</span>
              </span>
              <span>•</span>
              <span className="font-semibold text-emerald-700">
                ${job.min_salary ? job.min_salary.toLocaleString() : '100,000'} - ${job.max_salary ? job.max_salary.toLocaleString() : '160,000'}
              </span>
            </div>

            {/* Extracted Skill Badges */}
            <div className="flex flex-wrap gap-1 pt-1">
              {job.extracted_skills.slice(0, 5).map(skill => (
                <span key={skill} className="px-2 py-0.5 bg-white border border-border rounded text-[10px] font-medium text-text-primary">
                  {skill}
                </span>
              ))}
              {job.extracted_skills.length > 5 && (
                <span className="text-[10px] text-text-light font-semibold self-center">+ {job.extracted_skills.length - 5} more</span>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Detailed Modal Popup */}
      {selectedJob && (
        <div className="fixed inset-0 bg-sidebar/60 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-surface rounded-xl max-w-2xl w-full p-6 space-y-4 max-h-[90vh] overflow-y-auto shadow-2xl border border-border relative">
            <button 
              onClick={() => setSelectedJob(null)}
              className="absolute right-4 top-4 text-text-secondary hover:text-text-primary p-1"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="space-y-1">
              <span className="text-xs bg-primary/20 text-primary font-bold px-2 py-0.5 rounded">{selectedJob.job_category}</span>
              <h3 className="text-xl font-bold text-text-primary pt-1">{selectedJob.job_title}</h3>
              <p className="text-xs text-text-secondary font-medium">{selectedJob.company_name} • {selectedJob.city}, {selectedJob.country}</p>
            </div>

            <div className="p-3 bg-surface-mint rounded-lg border border-border flex items-center justify-between text-xs font-semibold text-sidebar">
              <span>Salary: ${selectedJob.min_salary?.toLocaleString()} - ${selectedJob.max_salary?.toLocaleString()} USD</span>
              <span>Experience: {selectedJob.experience_level}</span>
            </div>

            <div className="space-y-2">
              <h4 className="font-bold text-xs text-text-primary uppercase tracking-wider">Required & Extracted Skills</h4>
              <div className="flex flex-wrap gap-1.5">
                {selectedJob.extracted_skills.map(s => (
                  <span key={s} className="px-2.5 py-1 bg-sidebar text-white rounded text-xs font-medium">
                    {s}
                  </span>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <h4 className="font-bold text-xs text-text-primary uppercase tracking-wider">Job Description</h4>
              <p className="text-xs text-text-secondary leading-relaxed bg-surface-secondary p-3 rounded border border-border">
                {selectedJob.description}
              </p>
            </div>

            {/* Similar Jobs Recommendation */}
            {selectedJob.similar_jobs && selectedJob.similar_jobs.length > 0 && (
              <div className="space-y-2 pt-2 border-t border-border">
                <h4 className="font-bold text-xs text-text-primary flex items-center space-x-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-primary" />
                  <span>TF-IDF Similar Job Recommendations</span>
                </h4>
                <div className="space-y-1.5">
                  {selectedJob.similar_jobs.map(sj => (
                    <div key={sj.job_key} className="p-2 bg-surface-mint/30 rounded border border-border flex items-center justify-between text-xs">
                      <span className="font-semibold text-text-primary">{sj.job_title} ({sj.job_category})</span>
                      <span className="text-[10px] text-emerald-800 font-bold bg-emerald-100 px-2 py-0.5 rounded">
                        {(sj.similarity_score * 100).toFixed(0)}% Similarity
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
