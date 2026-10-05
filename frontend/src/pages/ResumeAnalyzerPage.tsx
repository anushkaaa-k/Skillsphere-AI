import React, { useState, useEffect } from 'react';
import { parseResume, fetchUserProfile, analyzeSkillGap } from '../services/api';
import { Upload, FileText, CheckCircle2, AlertCircle, ArrowRight, Plus, Check } from 'lucide-react';

interface ResumeAnalyzerPageProps {
  onProceedToGapStudio: () => void;
}

export const ResumeAnalyzerPage: React.FC<ResumeAnalyzerPageProps> = ({ onProceedToGapStudio }) => {
  const [file, setFile] = useState<File | null>(null);
  const [pastedText, setPastedText] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string>('');
  const [confirmedSkills, setConfirmedSkills] = useState<string[]>([]);
  const [targetRole, setTargetRole] = useState<string>('Data Scientist');
  const [expLevel, setExpLevel] = useState<string>('Mid Level');

  useEffect(() => {
    fetchUserProfile().then(p => {
      if (p) {
        setConfirmedSkills(p.confirmed_skills || []);
        if (p.target_role) setTargetRole(p.target_role);
        if (p.experience_level) setExpLevel(p.experience_level);
      }
    }).catch(console.error);
  }, []);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file && !pastedText.trim()) {
      setError("Please select a resume file (PDF/DOCX/TXT) or paste resume text.");
      return;
    }

    setError('');
    setLoading(true);

    try {
      const formData = new FormData();
      if (file) formData.append('file', file);
      if (pastedText) formData.append('pasted_text', pastedText);

      const res = await parseResume(formData);
      setResult(res);
    } catch (err: any) {
      setError(err.message || "Failed to parse resume.");
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmSkill = async (skill: string) => {
    const cleanKey = (s: string) => s.trim().toLowerCase().replace(/[\-_]+/g, ' ').replace(/\s+/g, ' ');
    const key = cleanKey(skill);
    if (!confirmedSkills.some(s => cleanKey(s) === key)) {
      const updated = [...confirmedSkills, skill];
      setConfirmedSkills(updated);
      try {
        await analyzeSkillGap(updated, targetRole, expLevel);
      } catch (err) {
        console.error("Error confirming skill:", err);
      }
    }
  };

  const handleConfirmAllDetected = async () => {
    if (!result || !result.detected_skills) return;
    const cleanKey = (s: string) => s.trim().toLowerCase().replace(/[\-_]+/g, ' ').replace(/\s+/g, ' ');
    const currentKeys = new Set(confirmedSkills.map(cleanKey));
    const toAdd = result.detected_skills.filter((s: string) => !currentKeys.has(cleanKey(s)));
    if (toAdd.length > 0) {
      const updated = [...confirmedSkills, ...toAdd];
      setConfirmedSkills(updated);
      try {
        await analyzeSkillGap(updated, targetRole, expLevel);
      } catch (err) {
        console.error("Error confirming all skills:", err);
      }
    }
  };

  const cleanKey = (s: string) => s.trim().toLowerCase().replace(/[\-_]+/g, ' ').replace(/\s+/g, ' ');
  const confirmedKeySet = new Set(confirmedSkills.map(cleanKey));

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header Info */}
      <div className="custom-card p-6 border-l-4 border-primary space-y-2">
        <h3 className="text-lg font-bold text-text-primary">Resume Parsing & Skill Extraction Pipeline</h3>
        <p className="text-xs text-text-secondary leading-relaxed">
          Upload your resume in PDF or DOCX format, or paste your career summary text directly. 
          SkillSphere AI extracts skills into detected suggestions. You manually choose which skills to confirm 
          so your Candidate Confirmed Skills list remains 100% accurate.
        </p>
      </div>

      {/* Input Form */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* File Upload Box */}
        <div className="custom-card p-6 space-y-4">
          <h4 className="font-bold text-sm text-text-primary flex items-center space-x-2">
            <Upload className="w-4 h-4 text-primary" />
            <span>Option 1: Upload Resume File</span>
          </h4>

          <div className="border-2 border-dashed border-border rounded-lg p-6 text-center hover:border-primary transition cursor-pointer bg-surface-mint/30">
            <input 
              type="file" 
              accept=".pdf,.docx,.doc,.txt"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="hidden" 
              id="resume-upload" 
            />
            <label htmlFor="resume-upload" className="cursor-pointer space-y-2 block">
              <FileText className="w-10 h-10 text-sidebar mx-auto opacity-75" />
              <p className="text-xs font-semibold text-text-primary">
                {file ? file.name : "Click to browse or drop file here"}
              </p>
              <p className="text-[11px] text-text-secondary">Supports PDF, DOCX, TXT (Max 10MB)</p>
            </label>
          </div>
        </div>

        {/* Text Paste Box */}
        <div className="custom-card p-6 space-y-4">
          <h4 className="font-bold text-sm text-text-primary flex items-center space-x-2">
            <FileText className="w-4 h-4 text-primary" />
            <span>Option 2: Paste Resume Text</span>
          </h4>

          <textarea 
            rows={5}
            placeholder="Paste your resume work experience, skills list, or career summary here..."
            value={pastedText}
            onChange={(e) => setPastedText(e.target.value)}
            className="input-field w-full text-xs"
          />
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-800 rounded-lg text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Action Button */}
      <div className="flex justify-end">
        <button 
          onClick={handleUpload}
          disabled={loading}
          className="btn-primary text-xs px-6 py-3 flex items-center space-x-2 shadow-sm"
        >
          <span>{loading ? "Parsing Resume Text..." : "Extract Skills & Analyze Resume"}</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Parsing Results Display */}
      {result && (
        <div className="custom-card p-6 space-y-5 border-t-4 border-emerald-600">
          <div className="flex items-center justify-between border-b border-border pb-3">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="w-5 h-5 text-emerald-600" />
              <h3 className="font-bold text-text-primary text-base">Resume Detection Results</h3>
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-xs bg-emerald-100 text-emerald-800 px-3 py-1 rounded-full font-semibold">
                {result.skill_count} Detected Skills
              </span>
              <button
                onClick={handleConfirmAllDetected}
                className="btn-primary text-[11px] py-1 px-3 flex items-center space-x-1"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Confirm All Detected Skills</span>
              </button>
            </div>
          </div>

          <p className="text-xs text-text-secondary italic">
            Detected skills are listed below. Click <b>+ Confirm</b> on any skill to add it to your Candidate Confirmed Skills.
          </p>

          {/* Extracted Skills Categories */}
          <div className="space-y-3">
            <h4 className="font-bold text-xs text-text-primary uppercase tracking-wider">Categorized Extracted Skills</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {Object.entries(result.categorized_skills || {}).map(([cat, skills]: [string, any]) => (
                <div key={cat} className="p-3 bg-surface-mint rounded-lg border border-border space-y-1.5">
                  <p className="text-xs font-bold text-sidebar">{cat}</p>
                  <div className="flex flex-wrap gap-1.5">
                    {skills.map((s: string) => {
                      const isConfirmed = confirmedKeySet.has(cleanKey(s));
                      return (
                        <div key={s} className="flex items-center space-x-1 bg-white border border-border rounded px-2 py-1 text-[11px] font-semibold text-text-primary">
                          <span>{s}</span>
                          {isConfirmed ? (
                            <span className="text-[10px] text-emerald-700 bg-emerald-50 px-1 rounded font-bold flex items-center space-x-0.5">
                              <Check className="w-3 h-3 text-emerald-600 inline" />
                              <span>Confirmed</span>
                            </span>
                          ) : (
                            <button 
                              onClick={() => handleConfirmSkill(s)} 
                              className="text-[10px] text-primary hover:text-sidebar font-bold ml-1 px-1 bg-surface-mint rounded border border-border"
                            >
                              + Confirm
                            </button>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Education & Experience Summary */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            <div className="p-3 bg-surface-secondary rounded-lg border border-border">
              <p className="text-xs font-semibold text-text-secondary">Education Detection:</p>
              <p className="text-xs font-bold text-text-primary mt-1">{result.education_summary?.join(", ")}</p>
            </div>
            <div className="p-3 bg-surface-secondary rounded-lg border border-border">
              <p className="text-xs font-semibold text-text-secondary">Estimated Experience Level:</p>
              <p className="text-xs font-bold text-text-primary mt-1">~{result.estimated_experience_years} Years Active Industry Skills</p>
            </div>
          </div>

          {/* Proceed Action */}
          <div className="pt-4 flex justify-end">
            <button 
              onClick={onProceedToGapStudio}
              className="btn-primary text-xs px-6 py-2.5 flex items-center space-x-2"
            >
              <span>Proceed to Skill Gap Studio ({confirmedSkills.length} Confirmed)</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
