import React, { useEffect, useState } from 'react';
import { analyzeSkillGap, fetchUserProfile, toggleSkillLearned } from '../services/api';
import { SkillGapAnalysisResult } from '../types';
import { Target, CheckCircle2, AlertTriangle, ArrowRight, Download, Check, Sparkles, BookOpen } from 'lucide-react';

export const SkillGapStudioPage: React.FC = () => {
  const [confirmedSkills, setConfirmedSkills] = useState<string[]>([]);
  const [targetRole, setTargetRole] = useState<string>("Data Scientist");
  const [expLevel, setExpLevel] = useState<string>("Mid Level");
  const [analysis, setAnalysis] = useState<SkillGapAnalysisResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [newSkillInput, setNewSkillInput] = useState<string>('');

  useEffect(() => {
    loadProfileAndAnalyze();
  }, []);

  const loadProfileAndAnalyze = async () => {
    setLoading(true);
    try {
      const profile = await fetchUserProfile();
      const skills = profile.confirmed_skills || [];
      const role = profile.target_role || "Data Scientist";
      setConfirmedSkills(skills);
      setTargetRole(role);

      const res = await analyzeSkillGap(skills, role, expLevel);
      setAnalysis(res);
    } catch (err) {
      console.error("Error loading skill gap profile:", err);
    } finally {
      setLoading(false);
    }
  };

  const runAnalysisWithSkills = async (skills: string[], role: string, exp: string) => {
    setLoading(true);
    try {
      const res = await analyzeSkillGap(skills, role, exp);
      setAnalysis(res);
      if (res.confirmed_skills_canonical && res.confirmed_skills_canonical.length > 0) {
        setConfirmedSkills(res.confirmed_skills_canonical);
      }
    } catch (err) {
      console.error("Error running gap analysis:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunAnalysis = () => {
    runAnalysisWithSkills(confirmedSkills, targetRole, expLevel);
  };

  const handleTargetRoleChange = (role: string) => {
    setTargetRole(role);
    runAnalysisWithSkills(confirmedSkills, role, expLevel);
  };

  const handleExpLevelChange = (exp: string) => {
    setExpLevel(exp);
    runAnalysisWithSkills(confirmedSkills, targetRole, exp);
  };

  const cleanKey = (s: string) => s.trim().toLowerCase().replace(/[\-_]+/g, ' ').replace(/\s+/g, ' ');

  const handleAddSkill = () => {
    const raw = newSkillInput.trim();
    if (!raw) return;
    const key = cleanKey(raw);
    const exists = confirmedSkills.some(s => cleanKey(s) === key);
    if (!exists) {
      const updated = [...confirmedSkills, raw];
      setConfirmedSkills(updated);
      setNewSkillInput('');
      runAnalysisWithSkills(updated, targetRole, expLevel);
    }
  };

  const handleRemoveSkill = (skill: string) => {
    const key = cleanKey(skill);
    const updated = confirmedSkills.filter(s => cleanKey(s) !== key);
    setConfirmedSkills(updated);
    runAnalysisWithSkills(updated, targetRole, expLevel);
  };

  const handleToggleLearned = async (skill: string) => {
    try {
      const res = await toggleSkillLearned(skill);
      if (res && res.analysis) {
        setAnalysis(res.analysis);
        if (res.confirmed_skills) {
          setConfirmedSkills(res.confirmed_skills);
        }
      } else {
        const exists = confirmedSkills.some(s => cleanKey(s) === cleanKey(skill));
        const updated = exists ? confirmedSkills : [...confirmedSkills, skill];
        runAnalysisWithSkills(updated, targetRole, expLevel);
      }
    } catch (err) {
      console.error("Error toggling learned skill:", err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Controls & Candidate Input Card */}
      <div className="custom-card p-5 space-y-4">
        <div className="flex items-center space-x-2 border-b border-border pb-3">
          <Target className="w-5 h-5 text-primary" />
          <h3 className="font-bold text-text-primary text-base">Candidate Profile & Target Role Configuration</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-semibold text-text-secondary mb-1">Select Target Role</label>
            <select 
              value={targetRole} 
              onChange={(e) => handleTargetRoleChange(e.target.value)}
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
            <label className="block text-xs font-semibold text-text-secondary mb-1">Target Experience Level</label>
            <select 
              value={expLevel} 
              onChange={(e) => handleExpLevelChange(e.target.value)}
              className="input-field w-full text-xs font-medium"
            >
              <option value="Entry Level">Entry Level</option>
              <option value="Mid Level">Mid Level</option>
              <option value="Senior Level">Senior Level</option>
            </select>
          </div>

          <div className="flex items-end">
            <button 
              onClick={handleRunAnalysis}
              disabled={loading}
              className="btn-primary w-full text-xs py-2.5 flex items-center justify-center space-x-2 shadow-xs"
            >
              <Sparkles className="w-4 h-4" />
              <span>{loading ? "Calculating Gap Score..." : "Recalculate Skill Gap"}</span>
            </button>
          </div>
        </div>

        {/* Confirmed Skills Chips */}
        <div className="space-y-2 pt-2">
          <label className="block text-xs font-semibold text-text-secondary">Candidate Confirmed Skills ({confirmedSkills.length})</label>
          <div className="flex flex-wrap gap-1.5 items-center">
            {confirmedSkills.map(skill => (
              <span key={skill} className="px-2.5 py-1 bg-surface-mint text-sidebar border border-border rounded-md text-xs font-semibold flex items-center space-x-1.5">
                <span>{skill}</span>
                <button onClick={() => handleRemoveSkill(skill)} className="text-text-secondary hover:text-rose-600 font-bold ml-1 text-xs">×</button>
              </span>
            ))}
            
            <div className="flex items-center space-x-1">
              <input 
                type="text" 
                placeholder="+ Add skill..."
                value={newSkillInput}
                onChange={(e) => setNewSkillInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleAddSkill()}
                className="input-field text-xs py-1 px-2 w-28"
              />
              <button onClick={handleAddSkill} className="btn-secondary text-xs py-1 px-2.5">+</button>
            </div>
          </div>
        </div>
      </div>

      {/* Analysis Results Display */}
      {analysis && (
        <div className="space-y-6">
          {/* Executive Coverage Score Card */}
          <div className="custom-card p-6 bg-gradient-to-r from-sidebar to-[#174d4d] text-white flex flex-col md:flex-row items-center justify-between gap-6 shadow-md">
            <div className="space-y-2">
              <span className="text-xs uppercase tracking-wider text-primary font-bold">Skill Gap Analysis Index</span>
              <h2 className="text-2xl font-bold">Skill Coverage Score for {analysis.target_role}</h2>
              <p className="text-xs text-sidebar-muted max-w-xl leading-relaxed">
                {analysis.methodology}
              </p>
            </div>

            <div className="flex items-center space-x-6 bg-white/10 p-4 rounded-xl border border-white/20">
              <div className="text-center">
                <span className="text-3xl font-extrabold text-primary">{analysis.coverage_percentage}%</span>
                <p className="text-[10px] text-sidebar-muted font-medium mt-1">Skill Coverage Ratio</p>
              </div>
              <div className="h-10 w-px bg-white/20" />
              <div className="text-center">
                <span className="text-2xl font-bold text-white">{analysis.matched_skills.length} / {analysis.total_target_skills_analyzed}</span>
                <p className="text-[10px] text-sidebar-muted font-medium mt-1">Matched Target Skills</p>
              </div>
            </div>
          </div>

          {/* High Priority Gaps & Roadmap Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* High Priority Skill Gaps */}
            <div className="custom-card p-5 space-y-4">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <h3 className="font-bold text-text-primary text-sm flex items-center space-x-2">
                  <AlertTriangle className="w-4 h-4 text-amber-600" />
                  <span>High-Priority Skill Gaps ({analysis.missing_high_priority.length})</span>
                </h3>
              </div>

              <div className="space-y-2.5 max-h-[420px] overflow-y-auto pr-1">
                {analysis.missing_high_priority.map((skill) => (
                  <div key={skill.skill_name} className="p-3 bg-surface-mint/50 border border-border rounded-lg flex items-center justify-between">
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-xs text-text-primary">{skill.skill_name}</span>
                        {skill.is_required && (
                          <span className="px-1.5 py-0.5 bg-amber-100 text-amber-800 text-[9px] font-bold rounded">Required</span>
                        )}
                      </div>
                      <p className="text-[11px] text-text-secondary mt-0.5">
                        Appears in <b>{skill.demand_percentage}%</b> of postings | Priority Score: {skill.priority_score}
                      </p>
                    </div>

                    <button 
                      onClick={() => handleToggleLearned(skill.skill_name)}
                      className="btn-secondary text-[11px] py-1 px-2.5 flex items-center space-x-1 hover:bg-emerald-100 hover:text-emerald-800"
                    >
                      <Check className="w-3 h-3" />
                      <span>Mark Learned</span>
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Prioritized Learning Roadmap */}
            <div className="custom-card p-5 space-y-4">
              <div className="flex items-center justify-between border-b border-border pb-3">
                <h3 className="font-bold text-text-primary text-sm flex items-center space-x-2">
                  <BookOpen className="w-4 h-4 text-sidebar" />
                  <span>Recommended Learning Sequence Roadmap</span>
                </h3>
                <a 
                  href={`/api/reports/pdf/skill-gap?target_role=${encodeURIComponent(targetRole)}`}
                  target="_blank"
                  rel="noreferrer"
                  className="btn-primary text-[11px] py-1 px-3 flex items-center space-x-1.5"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>PDF Report</span>
                </a>
              </div>

              <div className="space-y-3 max-h-[420px] overflow-y-auto pr-1">
                {analysis.roadmap.map((step) => (
                  <div key={step.step} className="p-3 bg-white border border-border rounded-lg space-y-1.5 shadow-2xs">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-sidebar flex items-center space-x-2">
                        <span className="w-5 h-5 rounded-full bg-primary text-white text-[10px] font-extrabold flex items-center justify-center">
                          {step.step}
                        </span>
                        <span>{step.skill_name}</span>
                      </span>
                      <span className="text-[10px] font-semibold text-text-secondary px-2 py-0.5 bg-surface-mint rounded">
                        {step.priority_level}
                      </span>
                    </div>
                    <p className="text-[11px] text-text-secondary italic">{step.evidence}</p>
                    {step.related_skills.length > 0 && (
                      <div className="flex items-center space-x-1 text-[10px] text-text-light pt-1">
                        <span>Related skills:</span>
                        <span className="font-semibold text-text-primary">{step.related_skills.join(", ")}</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
