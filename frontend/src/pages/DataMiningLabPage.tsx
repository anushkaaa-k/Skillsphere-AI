import React, { useState } from 'react';
import { runClassification, predictCategory, runClustering, runApriori, fetchTextMining } from '../services/api';
import { Cpu, Play, ScatterChart as ScatterIcon, Network, FileText, HelpCircle } from 'lucide-react';

const PracticalExplanation: React.FC<{
  title: string;
  why: string;
  input: string;
  whatHappens: string;
  output: string;
  howToRead: string;
}> = ({ title, why, input, whatHappens, output, howToRead }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="bg-surface-mint/70 border border-border rounded-lg p-3.5 text-xs space-y-2">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between font-bold text-sidebar hover:text-primary transition"
      >
        <span className="flex items-center space-x-2">
          <HelpCircle className="w-4 h-4 text-primary" />
          <span>Practical Context ({title})</span>
        </span>
        <span className="text-[11px] font-semibold text-primary px-2.5 py-0.5 bg-white border border-border rounded-md shadow-2xs">
          {isOpen ? "Hide Explanation ▲" : "Why this analysis? ▼"}
        </span>
      </button>

      {isOpen && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 pt-2.5 border-t border-border/60 text-text-primary text-[11px] leading-relaxed">
          <div className="space-y-1">
            <p className="font-bold text-sidebar uppercase text-[10px] tracking-wider">WHY THIS ANALYSIS?</p>
            <p className="text-text-secondary">{why}</p>
          </div>
          <div className="space-y-1">
            <p className="font-bold text-sidebar uppercase text-[10px] tracking-wider">INPUT DATA</p>
            <p className="text-text-secondary">{input}</p>
          </div>
          <div className="space-y-1">
            <p className="font-bold text-sidebar uppercase text-[10px] tracking-wider">WHAT HAPPENS?</p>
            <p className="text-text-secondary">{whatHappens}</p>
          </div>
          <div className="space-y-1">
            <p className="font-bold text-sidebar uppercase text-[10px] tracking-wider">OUTPUT & HOW TO READ IT</p>
            <p className="text-text-secondary"><b>Output:</b> {output}</p>
            <p className="text-text-secondary mt-0.5"><b>How to read:</b> {howToRead}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export const DataMiningLabPage: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<'classification' | 'clustering' | 'association' | 'text'>('classification');
  
  // Classification state
  const [clfAlgorithm, setClfAlgorithm] = useState<string>('decision_tree');
  const [clfResult, setClfResult] = useState<any>(null);
  const [customDescription, setCustomDescription] = useState<string>('');
  const [predictResult, setPredictResult] = useState<any>(null);

  // Clustering state
  const [numClusters, setNumClusters] = useState<number>(5);
  const [clusteringResult, setClusteringResult] = useState<any>(null);

  // Apriori state
  const [minSupport, setMinSupport] = useState<number>(0.08);
  const [minConfidence, setMinConfidence] = useState<number>(0.25);
  const [aprioriResult, setAprioriResult] = useState<any>(null);

  // Text mining state
  const [textMiningResult, setTextMiningResult] = useState<any>(null);

  const [loading, setLoading] = useState<boolean>(false);

  const handleTrainClassifier = async () => {
    setLoading(true);
    try {
      const res = await runClassification(clfAlgorithm);
      setClfResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handlePredictCategory = async () => {
    if (!customDescription.trim()) return;
    try {
      const res = await predictCategory(customDescription);
      setPredictResult(res);
    } catch (err) {
      console.error(err);
    }
  };

  const handleRunClustering = async () => {
    setLoading(true);
    try {
      const res = await runClustering(numClusters);
      setClusteringResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunApriori = async () => {
    setLoading(true);
    try {
      const res = await runApriori(minSupport, minConfidence);
      setAprioriResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunTextMining = async () => {
    setLoading(true);
    try {
      const res = await fetchTextMining();
      setTextMiningResult(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Sub-tab Navigation */}
      <div className="flex border-b border-border space-x-4 bg-surface p-2 rounded-lg">
        <button
          onClick={() => setActiveSubTab('classification')}
          className={`px-4 py-2 text-xs font-bold rounded-lg flex items-center space-x-2 transition ${
            activeSubTab === 'classification' ? 'bg-sidebar text-white' : 'text-text-secondary hover:bg-surface-mint'
          }`}
        >
          <Cpu className="w-4 h-4 text-primary" />
          <span>A. Classification</span>
        </button>

        <button
          onClick={() => setActiveSubTab('clustering')}
          className={`px-4 py-2 text-xs font-bold rounded-lg flex items-center space-x-2 transition ${
            activeSubTab === 'clustering' ? 'bg-sidebar text-white' : 'text-text-secondary hover:bg-surface-mint'
          }`}
        >
          <ScatterIcon className="w-4 h-4 text-primary" />
          <span>B. K-Means Clustering</span>
        </button>

        <button
          onClick={() => setActiveSubTab('association')}
          className={`px-4 py-2 text-xs font-bold rounded-lg flex items-center space-x-2 transition ${
            activeSubTab === 'association' ? 'bg-sidebar text-white' : 'text-text-secondary hover:bg-surface-mint'
          }`}
        >
          <Network className="w-4 h-4 text-primary" />
          <span>C. Apriori Association Rules</span>
        </button>

        <button
          onClick={() => setActiveSubTab('text')}
          className={`px-4 py-2 text-xs font-bold rounded-lg flex items-center space-x-2 transition ${
            activeSubTab === 'text' ? 'bg-sidebar text-white' : 'text-text-secondary hover:bg-surface-mint'
          }`}
        >
          <FileText className="w-4 h-4 text-primary" />
          <span>D. TF-IDF Text Mining</span>
        </button>
      </div>

      {/* TAB A: CLASSIFICATION */}
      {activeSubTab === 'classification' && (
        <div className="space-y-6">
          <div className="custom-card p-5 space-y-4">
            <h3 className="font-bold text-text-primary text-base">Job Category Classification Pipeline</h3>
            <p className="text-xs text-text-secondary leading-relaxed">
              Predict job categories from text using Decision Tree or Multinomial Naive Bayes classifiers. 
              Transforms text into TF-IDF vector representations with strict train/test split to prevent leakage.
            </p>

            <PracticalExplanation 
              title={clfAlgorithm === 'decision_tree' ? "Decision Tree Classification" : "Multinomial Naive Bayes Classification"}
              why="Used to predict the target job category (job_category) from features available in the job-posting data."
              input="Job-posting features such as skills, experience, education requirements, and TF-IDF text vectors."
              whatHappens="The model learns patterns from existing labelled job records and uses those patterns to classify a job description into a target job category (job_category)."
              output="Predicted target job category for a job description, model accuracy, precision, recall, and F1-score."
              howToRead="Higher accuracy and F1-score mean the model accurately assigns job descriptions to their correct job categories."
            />

            <div className="flex items-center space-x-4 pt-2">
              <select 
                value={clfAlgorithm} 
                onChange={(e) => setClfAlgorithm(e.target.value)}
                className="input-field text-xs font-medium w-64"
              >
                <option value="decision_tree">Decision Tree Classifier</option>
                <option value="naive_bayes">Multinomial Naive Bayes</option>
              </select>

              <button 
                onClick={handleTrainClassifier}
                disabled={loading}
                className="btn-primary text-xs px-5 py-2.5 flex items-center space-x-2"
              >
                <Play className="w-4 h-4" />
                <span>{loading ? "Training Classifier..." : "Train & Evaluate Model"}</span>
              </button>
            </div>
          </div>

          {clfResult && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Performance Metrics */}
              <div className="custom-card p-5 space-y-3">
                <h4 className="font-bold text-sm text-text-primary">Model Evaluation Metrics</h4>
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 bg-surface-mint rounded border border-border">
                    <p className="text-[11px] text-text-secondary font-semibold">Accuracy Score</p>
                    <p className="text-xl font-bold text-sidebar">{(clfResult.accuracy * 100).toFixed(2)}%</p>
                  </div>
                  <div className="p-3 bg-surface-mint rounded border border-border">
                    <p className="text-[11px] text-text-secondary font-semibold">F1-Score (Weighted)</p>
                    <p className="text-xl font-bold text-sidebar">{(clfResult.f1_score * 100).toFixed(2)}%</p>
                  </div>
                  <div className="p-3 bg-surface-mint rounded border border-border">
                    <p className="text-[11px] text-text-secondary font-semibold">Precision</p>
                    <p className="text-xl font-bold text-sidebar">{(clfResult.precision * 100).toFixed(2)}%</p>
                  </div>
                  <div className="p-3 bg-surface-mint rounded border border-border">
                    <p className="text-[11px] text-text-secondary font-semibold">Recall</p>
                    <p className="text-xl font-bold text-sidebar">{(clfResult.recall * 100).toFixed(2)}%</p>
                  </div>
                </div>
              </div>

              {/* Live Classifier */}
              <div className="custom-card p-5 space-y-3">
                <h4 className="font-bold text-sm text-text-primary">Live Category Classifier</h4>
                <textarea 
                  rows={3}
                  placeholder="Paste a job description here to classify..."
                  value={customDescription}
                  onChange={(e) => setCustomDescription(e.target.value)}
                  className="input-field w-full text-xs"
                />
                <button 
                  onClick={handlePredictCategory}
                  className="btn-primary text-xs px-4 py-2"
                >
                  Predict Category
                </button>

                {predictResult && (
                  <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-900 rounded text-xs">
                    Predicted Job Category: <b>{predictResult.predicted_category}</b>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB B: CLUSTERING */}
      {activeSubTab === 'clustering' && (
        <div className="space-y-6">
          <div className="custom-card p-5 space-y-4">
            <h3 className="font-bold text-text-primary text-base">K-Means Job Posting Clustering</h3>
            <p className="text-xs text-text-secondary leading-relaxed">
              Unsupervised clustering partitions job postings into distinct groups based on skill requirement similarities.
            </p>

            <PracticalExplanation 
              title={`K-Means Clustering (K=${numClusters})`}
              why="Groups job postings with similar skill and qualification profiles together in unsupervised clusters."
              input="Extracted skills and TF-IDF feature vectors from job descriptions."
              whatHappens={`Partitions the job-posting dataset into K=${numClusters} distinct clusters based on similarity in skill requirements.`}
              output="Cluster IDs, posting counts per cluster, dominant job category, and top characteristic keywords for each cluster."
              howToRead="Clusters show distinct job profile archetypes in the job market, helping identify skill sets that define role types."
            />

            <div className="flex items-center space-x-4 pt-2">
              <label className="text-xs font-semibold text-text-secondary">Number of Clusters K: {numClusters}</label>
              <input 
                type="range" 
                min={2} 
                max={8} 
                value={numClusters} 
                onChange={(e) => setNumClusters(Number(e.target.value))}
                className="w-48" 
              />
              <button 
                onClick={handleRunClustering}
                disabled={loading}
                className="btn-primary text-xs px-5 py-2 flex items-center space-x-2"
              >
                <Play className="w-4 h-4" />
                <span>{loading ? "Clustering..." : "Run K-Means Clustering"}</span>
              </button>
            </div>
          </div>

          {clusteringResult && (
            <div className="space-y-6">
              <div className="custom-card p-4 flex items-center justify-between text-xs">
                <span>Silhouette Score: <b>{clusteringResult.silhouette_score}</b></span>
                <span>Total Clusters Formed: <b>{clusteringResult.num_clusters}</b></span>
              </div>

              {/* Cluster Summaries */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {clusteringResult.cluster_summaries.map((c: any) => (
                  <div key={c.cluster_id} className="custom-card p-4 space-y-2">
                    <div className="flex justify-between items-center border-b border-border pb-2">
                      <span className="font-bold text-xs text-sidebar">Cluster #{c.cluster_id + 1} ({c.dominant_category})</span>
                      <span className="text-[10px] font-bold bg-primary text-white px-2 py-0.5 rounded">{c.size} postings ({c.percentage}%)</span>
                    </div>
                    <p className="text-[11px] text-text-secondary">Top Term Feature Keywords:</p>
                    <div className="flex flex-wrap gap-1">
                      {c.top_terms.map((term: string) => (
                        <span key={term} className="px-2 py-0.5 bg-surface-mint border border-border rounded text-[10px] font-semibold text-text-primary">
                          {term}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB C: ASSOCIATION RULES */}
      {activeSubTab === 'association' && (
        <div className="space-y-6">
          <div className="custom-card p-5 space-y-4">
            <h3 className="font-bold text-text-primary text-base">Apriori Skill Association Mining</h3>
            <p className="text-xs text-text-secondary leading-relaxed">
              Extract association rules to uncover which skills frequently co-occur in job postings.
            </p>

            <PracticalExplanation 
              title="Apriori Association Rule Mining"
              why="Discovers which skills frequently appear together in the same job postings."
              input="Skill sets extracted from each job posting in the database."
              whatHappens="Extracts frequent itemsets and generates association rules using minimum support and confidence thresholds."
              output="Skill co-occurrence rules (Antecedent ➜ Consequent) with Support, Confidence, and Lift values."
              howToRead="Support shows % of job postings containing both skills. Confidence shows likelihood of requiring Consequent when Antecedent is present. Lift > 1.0 indicates strong positive association."
            />

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
              <div>
                <label className="block text-xs font-semibold text-text-secondary mb-1">Min Support: {minSupport}</label>
                <input 
                  type="range" 
                  min={0.02} 
                  max={0.30} 
                  step={0.01} 
                  value={minSupport}
                  onChange={(e) => setMinSupport(Number(e.target.value))}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-text-secondary mb-1">Min Confidence: {minConfidence}</label>
                <input 
                  type="range" 
                  min={0.10} 
                  max={0.80} 
                  step={0.05} 
                  value={minConfidence}
                  onChange={(e) => setMinConfidence(Number(e.target.value))}
                  className="w-full"
                />
              </div>

              <div className="flex items-end">
                <button 
                  onClick={handleRunApriori}
                  disabled={loading}
                  className="btn-primary w-full text-xs py-2.5 flex items-center justify-center space-x-2"
                >
                  <Play className="w-4 h-4" />
                  <span>{loading ? "Extracting Rules..." : "Run Apriori Mining"}</span>
                </button>
              </div>
            </div>
          </div>

          {aprioriResult && (
            <div className="custom-card p-5 space-y-4">
              <div className="flex justify-between items-center">
                <h4 className="font-bold text-sm text-text-primary">Discovered Skill Association Rules ({aprioriResult.rule_count})</h4>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-sidebar text-white uppercase text-[10px]">
                      <th className="p-3 font-semibold">Antecedent Skill(s)</th>
                      <th className="p-3 font-semibold">Consequent Skill(s)</th>
                      <th className="p-3 font-semibold">Support</th>
                      <th className="p-3 font-semibold">Confidence</th>
                      <th className="p-3 font-semibold">Lift Metric</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    {aprioriResult.rules.map((rule: any, idx: number) => (
                      <tr key={idx} className="hover:bg-surface-mint/50">
                        <td className="p-3 font-bold text-text-primary">{rule.antecedent_str}</td>
                        <td className="p-3 font-bold text-primary">➜ {rule.consequent_str}</td>
                        <td className="p-3 text-text-secondary">{(rule.support * 100).toFixed(1)}%</td>
                        <td className="p-3 text-text-secondary">{(rule.confidence * 100).toFixed(1)}%</td>
                        <td className="p-3 font-bold text-emerald-700">{rule.lift}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB D: TEXT MINING */}
      {activeSubTab === 'text' && (
        <div className="space-y-6">
          <div className="custom-card p-5 space-y-4">
            <h3 className="font-bold text-text-primary text-base">TF-IDF Term Frequency Analysis</h3>
            <p className="text-xs text-text-secondary leading-relaxed">
              Analyze TF-IDF n-gram feature importance to surface key technical terms across postings.
            </p>

            <PracticalExplanation 
              title="TF-IDF Term Frequency Analysis"
              why="Identifies the most important and distinctive keywords across job descriptions."
              input="Raw text of job descriptions from the warehouse."
              whatHappens="Calculates Term Frequency-Inverse Document Frequency (TF-IDF) scores to weigh unique keywords higher than generic words."
              output="Top N-gram feature terms and their importance scores."
              howToRead="Higher TF-IDF scores highlight domain-specific technical terms and tools most emphasized in job postings."
            />

            <div className="pt-2">
              <button 
                onClick={handleRunTextMining}
                disabled={loading}
                className="btn-primary text-xs px-5 py-2 flex items-center space-x-2"
              >
                <Play className="w-4 h-4" />
                <span>{loading ? "Extracting TF-IDF Features..." : "Analyze Term Frequencies"}</span>
              </button>
            </div>
          </div>

          {textMiningResult && (
            <div className="custom-card p-5 space-y-3">
              <h4 className="font-bold text-sm text-text-primary">Top N-Gram TF-IDF Feature Keywords</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {textMiningResult.top_terms.map((t: any) => (
                  <div key={t.term} className="p-2 bg-surface-mint rounded border border-border flex justify-between items-center text-xs">
                    <span className="font-bold text-text-primary">{t.term}</span>
                    <span className="text-[10px] text-text-secondary font-semibold">{t.score}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
