import React, { useEffect, useState } from 'react';
import { fetchSystemSettings, triggerReseed } from '../services/api';
import { Settings, RefreshCw, CheckCircle2, ShieldAlert, Palette, Database } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [info, setInfo] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [msg, setMsg] = useState<string>('');

  useEffect(() => {
    loadInfo();
  }, []);

  const loadInfo = async () => {
    try {
      const data = await fetchSystemSettings();
      setInfo(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleReseed = async () => {
    if (!window.confirm("Are you sure you want to reset and reseed the Star Schema Data Warehouse?")) return;
    setLoading(true);
    setMsg('');
    try {
      const res = await triggerReseed();
      setMsg(res.message);
      loadInfo();
    } catch (err) {
      setMsg("Failed to reseed database.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="custom-card p-5 border-l-4 border-primary space-y-2">
        <h3 className="text-lg font-bold text-text-primary">Application Settings & DWM Platform Metadata</h3>
        <p className="text-xs text-text-secondary">
          System version configuration, taxonomy category mapping, database reseed engine, 
          and reference color design tokens.
        </p>
      </div>

      {msg && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-900 rounded-lg text-xs flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          <span>{msg}</span>
        </div>
      )}

      {/* System Status Grid */}
      {info && (
        <div className="custom-card p-5 space-y-4">
          <h4 className="font-bold text-sm text-text-primary flex items-center space-x-2">
            <Database className="w-4 h-4 text-primary" />
            <span>Data Warehouse Engine Status</span>
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div className="p-3 bg-surface-mint rounded border border-border">
              <span className="text-text-secondary">Warehouse Status:</span>
              <p className="font-bold text-emerald-700 mt-1">{info.warehouse_status}</p>
            </div>
            <div className="p-3 bg-surface-mint rounded border border-border">
              <span className="text-text-secondary">Job Dimension Records:</span>
              <p className="font-bold text-sidebar mt-1">{info.total_jobs_stored} Postings</p>
            </div>
            <div className="p-3 bg-surface-mint rounded border border-border">
              <span className="text-text-secondary">Recorded Fact Relationships:</span>
              <p className="font-bold text-sidebar mt-1">{info.total_facts_recorded} Facts</p>
            </div>
          </div>
        </div>
      )}

      {/* Reseed Action Card */}
      <div className="custom-card p-5 space-y-3 border border-amber-200 bg-amber-50/20">
        <h4 className="font-bold text-sm text-text-primary flex items-center space-x-2">
          <ShieldAlert className="w-4 h-4 text-amber-600" />
          <span>Reseed & Reset Data Warehouse</span>
        </h4>
        <p className="text-xs text-text-secondary">
          Drops existing tables and runs fresh ETL pipeline from raw JSON/CSV job posting dataset.
        </p>
        <button 
          onClick={handleReseed}
          disabled={loading}
          className="btn-primary text-xs px-5 py-2.5 flex items-center space-x-2"
        >
          <RefreshCw className="w-4 h-4" />
          <span>{loading ? "Reseeding Database..." : "Reset & Reseed Data Warehouse"}</span>
        </button>
      </div>

      {/* Design Token Reference Swatches */}
      <div className="custom-card p-5 space-y-3">
        <h4 className="font-bold text-sm text-text-primary flex items-center space-x-2">
          <Palette className="w-4 h-4 text-primary" />
          <span>Verified Design Token Color Palette Swatches</span>
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-xs">
          <div className="p-3 rounded bg-background border border-border text-center font-semibold text-sidebar">
            Pale Mint Background<br/><span className="text-[10px] opacity-75">#eef7f5</span>
          </div>
          <div className="p-3 rounded bg-sidebar text-white text-center font-semibold">
            Deep Muted Teal<br/><span className="text-[10px] opacity-75">#0f3838</span>
          </div>
          <div className="p-3 rounded bg-primary text-white text-center font-semibold">
            Mustard Yellow/Gold<br/><span className="text-[10px] opacity-75">#d99b00</span>
          </div>
          <div className="p-3 rounded bg-surface border border-border text-center font-semibold text-text-primary">
            White Card Surface<br/><span className="text-[10px] opacity-75">#ffffff</span>
          </div>
          <div className="p-3 rounded bg-input border border-border text-center font-semibold text-text-primary">
            Mint Input Surface<br/><span className="text-[10px] opacity-75">#e4f2ef</span>
          </div>
        </div>
      </div>
    </div>
  );
};
