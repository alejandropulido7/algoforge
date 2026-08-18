import React, { useState } from 'react';
import { BarChart2, Download, Check, AlertCircle } from 'lucide-react';
import Button from '../components/common/Button';
import styles from '../styles/pages.module.css';
import { ALL_INDICATORS } from '../components/configurator/StepIndicators';
import { downloadIndicatorsZip } from '../services/api';

const Indicators: React.FC = () => {
  const [downloading, setDownloading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleDownload = async () => {
    setDownloading(true);
    setSuccess(false);
    try {
      const blob = await downloadIndicatorsZip();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'AlgoForge_MT5_Indicators.zip';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
      setSuccess(true);
      setTimeout(() => setSuccess(false), 5000);
    } catch (err) {
      console.error(err);
      alert("Failed to export indicators ZIP.");
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className={styles.pageContainer}>
      <header className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <BarChart2 className="text-cyan" size={32} />
          Library Indicators
        </h1>
        <p className="text-slate-400 mt-2 max-w-3xl">
          AlgoForge relies on the Python <code className="text-cyan bg-slate-800 px-1 rounded">ta</code> library for discovery. 
          To achieve 100% mathematical parity in MetaTrader 5, export these custom indicators and install them in your MT5 terminal. Future EA generations will automatically use these indicators via <code className="text-cyan bg-slate-800 px-1 rounded">iCustom()</code>.
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2 bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
          <div className="p-4 border-b border-slate-700 bg-slate-800/50 flex justify-between items-center">
            <h2 className="font-semibold text-white">Supported Indicators</h2>
            <span className="text-xs text-slate-400">{ALL_INDICATORS.length} Indicators</span>
          </div>
          <div className="p-0">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-900 text-slate-400 text-xs uppercase">
                <tr>
                  <th className="px-6 py-3 font-medium">Indicator</th>
                  <th className="px-6 py-3 font-medium">Description</th>
                  <th className="px-6 py-3 font-medium text-center">Status</th>
                </tr>
              </thead>
              <tbody>
                {ALL_INDICATORS.map((ind, i) => (
                  <tr key={i} className="border-b border-slate-700/50 hover:bg-slate-700/20">
                    <td className="px-6 py-4 font-medium text-white">{ind.name}</td>
                    <td className="px-6 py-4 text-slate-400">{ind.desc}</td>
                    <td className="px-6 py-4 text-center">
                      <Check size={16} className="text-emerald inline" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-6">
            <h3 className="text-lg font-semibold text-white mb-2">Export Indicators</h3>
            <p className="text-sm text-slate-400 mb-6">
              Download the fully mapped MQL5 custom indicators. These perfectly replicate the mathematical smoothing and logic used during simulation.
            </p>
            <Button 
              className="w-full flex items-center justify-center gap-2" 
              onClick={handleDownload}
              isLoading={downloading}
            >
              {success ? <Check size={18} /> : <Download size={18} />}
              {success ? 'Downloaded!' : 'Download MT5 Indicators ZIP'}
            </Button>
          </div>

          <div className="bg-amber-900/20 border border-amber-700/50 rounded-xl p-5">
            <div className="flex gap-3 mb-3">
              <AlertCircle className="text-amber shrink-0" size={20} />
              <h4 className="font-semibold text-amber">Installation Instructions</h4>
            </div>
            <ol className="list-decimal list-inside text-sm text-amber-200/80 space-y-2 ml-1">
              <li>Download the indicators ZIP package.</li>
              <li>Open MetaTrader 5 and go to <strong className="text-amber-100">File &gt; Open Data Folder</strong>.</li>
              <li>Navigate to <strong className="text-amber-100">MQL5 \ Indicators</strong>.</li>
              <li>Extract the ZIP here. It will create the <strong className="text-white bg-amber-900/50 px-1 rounded">AlgoForge\</strong> directory with its subfolders (<code className="text-cyan text-xs">Momentum</code>, <code className="text-cyan text-xs">Trend</code>, <code className="text-cyan text-xs">Volatility</code>, <code className="text-cyan text-xs">Volume</code>, <code className="text-cyan text-xs">Others</code>).</li>
              <li>In MetaTrader 5, press <kbd className="bg-slate-800 px-1.5 py-0.5 rounded text-xs text-white">F4</kbd> to open MetaEditor.</li>
              <li>In Navigator, right click on the <strong className="text-amber-100">AlgoForge</strong> indicators folder and click <strong className="text-amber-100">Compile</strong> (or restart MT5).</li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Indicators;
