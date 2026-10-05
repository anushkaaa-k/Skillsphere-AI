import React, { useEffect, useState } from 'react';
import { FileDown, FileText, Database, Network, ShieldCheck } from 'lucide-react';
import { fetchUserProfile } from '../services/api';

export const ReportsPage: React.FC = () => {
  const [profile, setProfile] = useState<any>(null);

  useEffect(() => {
    fetchUserProfile().then(setProfile).catch(console.error);
  }, []);

  const pdfUrl = profile?.target_role 
    ? `/api/reports/pdf/skill-gap?target_role=${encodeURIComponent(profile.target_role)}`
    : '/api/reports/pdf/skill-gap';

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="custom-card p-5 border-l-4 border-primary space-y-2">
        <h3 className="text-lg font-bold text-text-primary">Analytical Export & PDF Report Center</h3>
        <p className="text-xs text-text-secondary leading-relaxed">
          Generate comprehensive academic and executive reports grounded directly in warehouse facts 
          and data mining algorithms. All exports match SkillSphere AI's visual design palette.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* PDF Skill Gap Report Card */}
        <div className="custom-card p-6 space-y-4 hover:border-primary transition">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-surface-mint rounded-lg text-primary">
              <FileText className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-bold text-sm text-text-primary">PDF Personalized Skill Gap Report</h4>
              <p className="text-xs text-text-secondary">Executive candidate skill coverage evaluation</p>
            </div>
          </div>
          <p className="text-xs text-text-secondary leading-relaxed">
            Includes candidate target role ({profile?.target_role || 'Configured Role'}), matched competencies, high priority missing skills, 
            market demand evidence, and prioritized learning sequence.
          </p>
          <a 
            href={pdfUrl}
            target="_blank"
            rel="noreferrer"
            className="btn-primary w-full text-xs py-2.5 flex items-center justify-center space-x-2"
          >
            <FileDown className="w-4 h-4" />
            <span>Download PDF Report {profile?.target_role ? `(${profile.target_role})` : ''}</span>
          </a>
        </div>

        {/* CSV Skill Demand Export */}
        <div className="custom-card p-6 space-y-4 hover:border-primary transition">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-surface-mint rounded-lg text-sidebar">
              <Database className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-bold text-sm text-text-primary">CSV Skill Demand Matrix Export</h4>
              <p className="text-xs text-text-secondary">Granular skill volume and average salaries</p>
            </div>
          </div>
          <p className="text-xs text-text-secondary leading-relaxed">
            Export all canonical skill frequency metrics, job categories, and average salary distributions.
          </p>
          <a 
            href="/api/reports/csv/skill-demand"
            target="_blank"
            rel="noreferrer"
            className="btn-secondary w-full text-xs py-2.5 flex items-center justify-center space-x-2"
          >
            <FileDown className="w-4 h-4" />
            <span>Export Skill Demand CSV</span>
          </a>
        </div>

        {/* CSV Association Rules Export */}
        <div className="custom-card p-6 space-y-4 hover:border-primary transition">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-surface-mint rounded-lg text-amber-600">
              <Network className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-bold text-sm text-text-primary">Apriori Association Rules CSV</h4>
              <p className="text-xs text-text-secondary">Support, Confidence, and Lift calculations</p>
            </div>
          </div>
          <p className="text-xs text-text-secondary leading-relaxed">
            Download full list of mined skill co-occurrence rules extracted from job posting transactions.
          </p>
          <a 
            href="/api/reports/csv/association-rules"
            target="_blank"
            rel="noreferrer"
            className="btn-secondary w-full text-xs py-2.5 flex items-center justify-center space-x-2"
          >
            <FileDown className="w-4 h-4" />
            <span>Export Association Rules CSV</span>
          </a>
        </div>

        {/* OLAP Query CSV Export */}
        <div className="custom-card p-6 space-y-4 hover:border-primary transition">
          <div className="flex items-center space-x-3">
            <div className="p-3 bg-surface-mint rounded-lg text-emerald-600">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-bold text-sm text-text-primary">Multidimensional OLAP Results CSV</h4>
              <p className="text-xs text-text-secondary">Roll-up, drill-down, slice, dice data tables</p>
            </div>
          </div>
          <p className="text-xs text-text-secondary leading-relaxed">
            Export multidimensional analytical star schema sub-cubes for research or offline presentation.
          </p>
          <a 
            href="/api/reports/csv/olap?operation_type=slice"
            target="_blank"
            rel="noreferrer"
            className="btn-secondary w-full text-xs py-2.5 flex items-center justify-center space-x-2"
          >
            <FileDown className="w-4 h-4" />
            <span>Export OLAP Query CSV</span>
          </a>
        </div>
      </div>
    </div>
  );
};
