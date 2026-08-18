import { supabase } from './supabaseClient';
import type { Job, JobConfig } from '../types/job';
import type { Strategy } from '../types/strategy';
import type { OHLCVBar, DataSource } from '../types/data';

const rawApiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_URL = rawApiUrl.endsWith('/api') ? rawApiUrl : `${rawApiUrl}/api`;

const getAuthHeaders = async (): Promise<HeadersInit> => {
  const { data: { session } } = await supabase.auth.getSession();
  return {
    'Content-Type': 'application/json',
    ...(session ? { 'Authorization': `Bearer ${session.access_token}` } : {})
  };
};

export const fetchOHLCV = async (config: {
  symbol: string;
  timeframe: string;
  startDate?: string;
  endDate?: string;
  source?: string;
}): Promise<{ success: boolean; data: OHLCVBar[]; row_count: number; symbol: string; timeframe: string }> => {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/data/fetch`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      symbol: config.symbol,
      timeframe: config.timeframe,
      startDate: config.startDate,
      endDate: config.endDate,
      source: config.source || 'yfinance'
    })
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Failed to fetch data' }));
    throw new Error(err.detail || 'Failed to fetch data');
  }
  return response.json();
};

export const uploadCSV = async (file: File): Promise<{
  success: boolean;
  row_count: number;
  symbol: string;
  timeframe: string;
  dataset: DataSource;
}> => {
  const { data: { session } } = await supabase.auth.getSession();
  const headers: HeadersInit = {};
  if (session) {
    headers['Authorization'] = `Bearer ${session.access_token}`;
  }
  
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_URL}/data/upload`, {
    method: 'POST',
    headers,
    body: formData
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Failed to upload CSV' }));
    throw new Error(err.detail || 'Failed to upload file');
  }
  return response.json();
};

export const getDatasets = async (): Promise<DataSource[]> => {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/data/datasets`, { headers });
  if (!response.ok) throw new Error('Failed to fetch datasets');
  const res = await response.json();
  return res.datasets || [];
};

export const deleteDataset = async (datasetId: string): Promise<void> => {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/data/datasets/${datasetId}`, { method: 'DELETE', headers });
  if (!response.ok) throw new Error('Failed to delete dataset');
};

export interface SymbolItem {
  symbol: string;
  name: string;
  type: string;
  provider?: string;
  category?: string;
}

export const getSymbols = async (provider?: string): Promise<SymbolItem[]> => {
  const headers = await getAuthHeaders();
  const url = provider ? `${API_URL}/data/symbols?provider=${encodeURIComponent(provider)}` : `${API_URL}/data/symbols`;
  const response = await fetch(url, { headers });
  if (!response.ok) return [];
  const res = await response.json();
  return res.symbols || [];
};

export const createJob = async (config: JobConfig): Promise<Job> => {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/jobs`, {
    method: 'POST',
    headers,
    body: JSON.stringify(config)
  });
  if (!response.ok) throw new Error('Failed to create job');
  return response.json();
};

export const getJobs = async (): Promise<Job[]> => {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/jobs`, { headers });
  if (!response.ok) throw new Error('Failed to fetch jobs');
  return response.json();
};

export const getJob = async (id: string): Promise<Job> => {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/jobs/${id}`, { headers });
  if (!response.ok) throw new Error('Failed to fetch job');
  return response.json();
};

export const deleteJob = async (id: string): Promise<void> => {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/jobs/${id}`, { method: 'DELETE', headers });
  if (!response.ok) throw new Error('Failed to delete job');
};

export const getStrategies = async (jobId: string): Promise<Strategy[]> => {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/strategies?job_id=${jobId}`, { headers });
  if (!response.ok) throw new Error('Failed to fetch strategies');
  return response.json();
};

export const getStrategy = async (id: string): Promise<Strategy> => {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/strategies/${id}`, { headers });
  if (!response.ok) throw new Error('Failed to fetch strategy');
  return response.json();
};

export const exportStrategy = async (id: string, format: string): Promise<{ code: string }> => {
  const headers = await getAuthHeaders();
  const response = await fetch(`${API_URL}/export/${id}/${format}`, { headers });
  if (!response.ok) throw new Error('Failed to export strategy');
  return response.json();
};

export const downloadOnnxModel = async (strategyId: string): Promise<Blob> => {
  const { data: { session } } = await supabase.auth.getSession();
  const headers: HeadersInit = {};
  if (session) {
    headers['Authorization'] = `Bearer ${session.access_token}`;
  }
  const response = await fetch(`${API_URL}/export/${strategyId}/onnx`, { headers });
  if (!response.ok) throw new Error('Failed to download ONNX model file');
  return response.blob();
};
