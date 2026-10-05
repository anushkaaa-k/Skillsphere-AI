import React, { useState } from 'react';
import { runOlapQuery } from '../services/api';
import { OlapQueryResult } from '../types';
import { Database, Play, Download, Code, Layers } from 'lucide-react';

export const WarehouseExplorerPage: React.FC = () => {
  const [operationType, setOperationType] = useState<string>('slice');
  const [category, setCategory] = useState<string>('Data Science & Analytics');
  const [jobTitle, setJobTitle] = useState<string>('');
  const [city, setCity] = useState<string>('');
  const [year, setYear] = useState<string>('');
  const [olapResult, setOlapResult] = useState<OlapQueryResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const handleExecuteOlap = async () => {
    setLoading(true);
    try {
      const payload: any = { operation_type: operationType };
      if (category) payload.category = category;
      if (jobTitle) payload.job_title = jobTitle;
      if (city) payload.location_city = city;
      if (year) payload.year = Number(year);

      const res = await runOlapQuery(payload);
      setOlapResult(res);
    } catch (err) {
      console.error("Error running OLAP operation:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* OLAP Control Panel */}
      <div className="custom-card p-5 space-y-4">
        <div className="flex items-center space-x-2 border-b border-border pb-3">
          <Database className="w-5 h-5 text-primary" />
          <h3 className="font-bold text-text-primary text-base">Multidimensional Star Schema OLAP Query Engine</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-xs font-semibold text-text-secondary mb-1">OLAP Operation</label>
            <select 
              value={operationType} 
              onChange={(e) => setOperationType(e.target.value)}
              className="input-field w-full text-xs font-medium"
            >
              <option value="slice">1. Slice (Fix 1 Category Dimension)</option>
              <option value="rollup">2. Roll-Up (Monthly to Yearly Summary)</option>
              <option value="drilldown">3. Drill-Down (Category ➔ Role ➔ Skill)</option>
              <option value="dice">4. Dice (Multi-Dimension Sub-Cube)</option>
              <option value="pivot">5. Pivot (Skill vs Category Matrix)</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-text-secondary mb-1">Category Dimension</label>
            <select 
              value={category} 
              onChange={(e) => setCategory(e.target.value)}
              className="input-field w-full text-xs font-medium"
            >
              <option value="">All Categories</option>
              <option value="Data Science & Analytics">Data Science & Analytics</option>
              <option value="Software Engineering">Software Engineering</option>
              <option value="Machine Learning & AI">Machine Learning & AI</option>
              <option value="DevOps & Cloud Engineering">DevOps & Cloud</option>
              <option value="Data Engineering">Data Engineering</option>
              <option value="Cybersecurity">Cybersecurity</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-text-secondary mb-1">Location City</label>
            <select 
              value={city} 
              onChange={(e) => setCity(e.target.value)}
              className="input-field w-full text-xs font-medium"
            >
              <option value="">All Cities</option>
              <option value="San Francisco">San Francisco</option>
              <option value="New York">New York</option>
              <option value="Austin">Austin</option>
              <option value="Seattle">Seattle</option>
              <option value="London">London</option>
              <option value="Bengaluru">Bengaluru</option>
            </select>
          </div>

          <div className="flex items-end">
            <button 
              onClick={handleExecuteOlap}
              disabled={loading}
              className="btn-primary w-full text-xs py-2.5 flex items-center justify-center space-x-2 shadow-xs"
            >
              <Play className="w-4 h-4" />
              <span>{loading ? "Executing SQL Query..." : "Execute OLAP SQL"}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Query Results */}
      {olapResult && (
        <div className="custom-card p-5 space-y-4">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-border pb-3">
            <div>
              <h4 className="font-bold text-sm text-text-primary capitalize">
                OLAP {olapResult.operation} Query Output ({olapResult.record_count} Records)
              </h4>
              <p className="text-xs text-text-secondary mt-0.5">{olapResult.explanation}</p>
            </div>

            <a 
              href={`/api/reports/csv/olap?operation_type=${olapResult.operation}&category=${encodeURIComponent(category)}`}
              target="_blank"
              rel="noreferrer"
              className="btn-secondary text-xs py-1.5 px-3 flex items-center space-x-1.5"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export CSV</span>
            </a>
          </div>

          {/* SQL Snippet Box */}
          <div className="p-3 bg-sidebar text-emerald-300 rounded font-mono text-xs overflow-x-auto border border-sidebar-hover flex items-start space-x-2">
            <Code className="w-4 h-4 text-primary flex-shrink-0 mt-0.5" />
            <code>{olapResult.sql_snippet}</code>
          </div>

          {/* Query Output Data Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-sidebar text-white uppercase text-[10px]">
                  {olapResult.data.length > 0 && Object.keys(olapResult.data[0]).map((key) => (
                    <th key={key} className="p-3 font-semibold capitalize">{key.replace('_', ' ')}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {olapResult.data.map((row, idx) => (
                  <tr key={idx} className="hover:bg-surface-mint/50">
                    {Object.values(row).map((val: any, vIdx) => (
                      <td key={vIdx} className="p-3 font-medium text-text-primary">
                        {typeof val === 'number' && val > 1000 ? val.toLocaleString() : String(val)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
