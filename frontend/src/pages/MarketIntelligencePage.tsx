import React, { useEffect, useState } from 'react';
import { fetchSkillsDemand, compareRoles } from '../services/api';
import { SkillDemandItem } from '../types';
import { Search, ArrowUpDown, GitCompare, DollarSign, Layers } from 'lucide-react';

export const MarketIntelligencePage: React.FC = () => {
  const [skills, setSkills] = useState<SkillDemandItem[]>([]);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedCity, setSelectedCity] = useState<string>('');
  const [expLevel, setExpLevel] = useState<string>('');
  
  // Role comparison state
  const [role1, setRole1] = useState<string>('Data Scientist');
  const [role2, setRole2] = useState<string>('Software Engineer');
  const [comparisonResult, setComparisonResult] = useState<any>(null);
  const [loadingCompare, setLoadingCompare] = useState<boolean>(false);

  useEffect(() => {
    loadSkills();
  }, [selectedCategory, selectedCity, expLevel]);

  const loadSkills = async () => {
    try {
      const data = await fetchSkillsDemand(selectedCategory, selectedCity, expLevel);
      setSkills(data);
    } catch (err) {
      console.error("Error loading market intelligence skills:", err);
    }
  };

  const handleRunComparison = async () => {
    setLoadingCompare(true);
    try {
      const res = await compareRoles(role1, role2);
      setComparisonResult(res);
    } catch (err) {
      console.error("Error running role comparison:", err);
    } finally {
      setLoadingCompare(false);
    }
  };

  const filteredSkills = skills.filter(s => 
    s.skill.toLowerCase().includes(searchTerm.toLowerCase()) || 
    s.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Role Comparison Tool Card */}
      <div className="custom-card p-5 space-y-4">
        <div className="flex items-center space-x-2 border-b border-border pb-3">
          <GitCompare className="w-5 h-5 text-primary" />
          <h3 className="font-bold text-text-primary text-base">Job Role Skill & Salary Comparison Tool</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
          <div>
            <label className="block text-xs font-semibold text-text-secondary mb-1">Target Role 1</label>
            <select 
              value={role1} 
              onChange={(e) => setRole1(e.target.value)}
              className="input-field w-full text-xs font-medium"
            >
              <option value="Data Scientist">Data Scientist</option>
              <option value="Software Engineer">Software Engineer</option>
              <option value="Machine Learning Engineer">Machine Learning Engineer</option>
              <option value="DevOps Engineer">DevOps Engineer</option>
              <option value="Data Engineer">Data Engineer</option>
              <option value="Cybersecurity Analyst">Cybersecurity Analyst</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-text-secondary mb-1">Target Role 2</label>
            <select 
              value={role2} 
              onChange={(e) => setRole2(e.target.value)}
              className="input-field w-full text-xs font-medium"
            >
              <option value="Software Engineer">Software Engineer</option>
              <option value="Data Scientist">Data Scientist</option>
              <option value="Data Engineer">Data Engineer</option>
              <option value="Machine Learning Engineer">Machine Learning Engineer</option>
              <option value="DevOps Engineer">DevOps Engineer</option>
              <option value="Product Manager">Product Manager</option>
            </select>
          </div>

          <button 
            onClick={handleRunComparison}
            disabled={loadingCompare}
            className="btn-primary w-full text-xs py-2.5 flex items-center justify-center space-x-2"
          >
            <GitCompare className="w-4 h-4" />
            <span>{loadingCompare ? "Comparing Roles..." : "Compare Roles"}</span>
          </button>
        </div>

        {comparisonResult && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-3">
            {/* Role 1 Details */}
            <div className="p-4 bg-surface-mint rounded-lg border border-border space-y-2">
              <h4 className="font-bold text-sidebar text-sm">{comparisonResult.role_1.role}</h4>
              <p className="text-xs text-text-secondary">Posting Volume: <b>{comparisonResult.role_1.posting_volume} postings</b></p>
              <p className="text-xs text-text-secondary">Avg Salary Range: <b>${comparisonResult.role_1.avg_min_sal?.toLocaleString()} - ${comparisonResult.role_1.avg_max_sal?.toLocaleString()}</b></p>
              <div className="pt-2">
                <p className="text-xs font-semibold text-text-primary mb-1">Top Required Skills:</p>
                <div className="flex flex-wrap gap-1">
                  {comparisonResult.role_1.top_skills.map((s: any) => (
                    <span key={s.skill} className="px-2 py-0.5 bg-white border border-border rounded text-[11px] font-medium text-sidebar">
                      {s.skill} ({s.count})
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Role 2 Details */}
            <div className="p-4 bg-surface-mint rounded-lg border border-border space-y-2">
              <h4 className="font-bold text-sidebar text-sm">{comparisonResult.role_2.role}</h4>
              <p className="text-xs text-text-secondary">Posting Volume: <b>{comparisonResult.role_2.posting_volume} postings</b></p>
              <p className="text-xs text-text-secondary">Avg Salary Range: <b>${comparisonResult.role_2.avg_min_sal?.toLocaleString()} - ${comparisonResult.role_2.avg_max_sal?.toLocaleString()}</b></p>
              <div className="pt-2">
                <p className="text-xs font-semibold text-text-primary mb-1">Top Required Skills:</p>
                <div className="flex flex-wrap gap-1">
                  {comparisonResult.role_2.top_skills.map((s: any) => (
                    <span key={s.skill} className="px-2 py-0.5 bg-white border border-border rounded text-[11px] font-medium text-sidebar">
                      {s.skill} ({s.count})
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Skill Demand Table Card */}
      <div className="custom-card p-5 space-y-4">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
          <h3 className="font-bold text-text-primary text-base">Skill Demand Matrix & Salary Statistics</h3>
          <div className="flex items-center space-x-3">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-2.5 text-text-secondary" />
              <input 
                type="text" 
                placeholder="Search skills or categories..." 
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input-field pl-9 text-xs w-64"
              />
            </div>

            <select 
              value={selectedCategory} 
              onChange={(e) => setSelectedCategory(e.target.value)}
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
          </div>
        </div>

        {/* Data Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="bg-sidebar text-white uppercase text-[10px] tracking-wider">
                <th className="p-3 font-semibold">Canonical Skill</th>
                <th className="p-3 font-semibold">Skill Category</th>
                <th className="p-3 font-semibold">Posting Demand Volume</th>
                <th className="p-3 font-semibold">Est. Average Salary (USD)</th>
                <th className="p-3 font-semibold">Demand Level</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filteredSkills.slice(0, 30).map((item) => (
                <tr key={item.skill} className="hover:bg-surface-mint/50 transition">
                  <td className="p-3 font-bold text-text-primary">{item.skill}</td>
                  <td className="p-3 text-text-secondary">{item.category}</td>
                  <td className="p-3 font-semibold text-sidebar">{item.posting_count} postings</td>
                  <td className="p-3 font-semibold text-emerald-700">${item.avg_salary ? item.avg_salary.toLocaleString() : '135,000'}</td>
                  <td className="p-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                      item.posting_count > 100 
                        ? 'bg-amber-100 text-amber-800 border border-amber-300' 
                        : 'bg-teal-100 text-teal-800 border border-teal-300'
                    }`}>
                      {item.posting_count > 100 ? 'High Demand' : 'Standard'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
