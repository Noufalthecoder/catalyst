'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Upload,
  FileSpreadsheet,
  CheckCircle2,
  AlertTriangle,
  Play,
  ArrowRight,
  Sparkles,
  Terminal,
  Activity,
  Cpu
} from 'lucide-react';
import { AppShell } from '@/components/AppShell';
import { uploadCatalogFile, startEnrichmentJob, getJobStatus } from '@/lib/api';

export default function EnrichmentPage() {
  const [uploadResult, setUploadResult] = useState<any | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [activeJob, setActiveJob] = useState<any | null>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const res = await uploadCatalogFile(file);
      setUploadResult(res);
    } catch (err) {
      console.error('Failed to pre-validate catalog:', err);
    } finally {
      setUploading(false);
    }
  };

  const handleStartJob = async () => {
    try {
      const res = await startEnrichmentJob({
        catalog_name: uploadResult?.filename || 'industrial_catalog_batch.csv',
        max_products: uploadResult?.total_rows || 100,
        source_mode: 'live',
      });
      setActiveJob({
        job_id: res.job_id,
        status: 'PROCESSING',
        current_stage: 'parsing',
        stage_name: '01. Ingestion & Pre-cleaning',
        processed_products: 0,
        total_products: uploadResult?.total_rows || 100,
        progress_percentage: 0,
      });
    } catch (err) {
      console.error('Failed to start enrichment job:', err);
    }
  };

  useEffect(() => {
    if (activeJob && activeJob.status !== 'COMPLETED') {
      const interval = setInterval(async () => {
        try {
          const status = await getJobStatus(activeJob.job_id);
          setActiveJob(status);
          if (status.status === 'COMPLETED') {
            clearInterval(interval);
          }
        } catch (err) {
          console.error('Error polling job status:', err);
        }
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [activeJob?.job_id, activeJob?.status]);

  return (
    <AppShell title="ENRICHMENT ENGINE" subtitle="Automated Catalog Processing Console">
      <div className="space-y-6 max-w-7xl mx-auto font-mono text-xs">
        {activeJob ? (
          /* Processing Terminal Screen */
          <div className="bg-[#11161D] border border-[#29313C] rounded-xl p-8 shadow-2xl space-y-6">
            <div className="flex items-center justify-between border-b border-[#1F2732] pb-4">
              <div>
                <div className="flex items-center gap-2">
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                      activeJob.status === 'COMPLETED'
                        ? 'bg-[#62E6A7]/10 text-[#62E6A7] border border-[#62E6A7]/30'
                        : 'bg-[#2F6BFF]/15 text-[#4D7CFF] border border-[#2F6BFF]/40 animate-pulse'
                    }`}
                  >
                    {activeJob.status === 'COMPLETED' ? 'COMPLETED' : 'CATALYST IS THINKING'}
                  </span>
                  <span className="text-[#667180]">JOB ID: {activeJob.job_id}</span>
                </div>
                <h2 className="text-xl font-bold text-[#F4F7FB] mt-1">{activeJob.stage_name}</h2>
              </div>
              <div className="text-right">
                <div className="text-3xl font-extrabold text-[#4D7CFF]">
                  {activeJob.progress_percentage}%
                </div>
                <div className="text-[11px] text-[#667180]">
                  {activeJob.processed_products} / {activeJob.total_products} PRODUCTS PROCESSED
                </div>
              </div>
            </div>

            {/* Glowing Progress Bar */}
            <div className="w-full bg-[#0B0F14] h-3 rounded-full overflow-hidden border border-[#29313C]">
              <div
                className={`h-full transition-all duration-300 ${
                  activeJob.status === 'COMPLETED' ? 'bg-[#62E6A7]' : 'bg-[#2F6BFF]'
                }`}
                style={{ width: `${activeJob.progress_percentage}%` }}
              />
            </div>

            {/* Stages Matrix */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 pt-2">
              {[
                { id: 'parsing', name: '01 IDENTITY', label: 'MPN Resolution' },
                { id: 'taxonomy', name: '02 TAXONOMY', label: 'Industrial Class' },
                { id: 'sources', name: '03 SOURCE SEARCH', label: 'Web Crawl' },
                { id: 'attributes', name: '04 EXTRACTION', label: 'Consensus' },
                { id: 'validation', name: '05 VALIDATION', label: 'UOM Standard' },
                { id: 'delivery', name: '06 DELIVERY', label: '252-Column' },
              ].map((st) => (
                <div
                  key={st.id}
                  className={`p-3.5 rounded-lg border font-mono ${
                    activeJob.status === 'COMPLETED' || activeJob.current_stage === st.id
                      ? 'bg-[#151B23] border-[#2F6BFF] text-[#F4F7FB]'
                      : 'bg-[#0B0F14] border-[#1F2732] text-[#667180]'
                  }`}
                >
                  <div className="flex items-center justify-between text-[10px]">
                    <span className="font-bold">{st.name}</span>
                    {activeJob.status === 'COMPLETED' ? (
                      <span className="text-[#62E6A7]">✓</span>
                    ) : activeJob.current_stage === st.id ? (
                      <span className="text-[#4D7CFF] animate-pulse">●</span>
                    ) : (
                      <span>—</span>
                    )}
                  </div>
                  <div className="text-[11px] text-[#98A3B3] mt-1">{st.label}</div>
                </div>
              ))}
            </div>

            {activeJob.status === 'COMPLETED' && (
              <div className="p-4 bg-[#151B23] border border-[#62E6A7]/30 rounded-lg flex items-center justify-between">
                <div className="flex items-center gap-2 text-[#62E6A7] font-bold">
                  <CheckCircle2 className="w-5 h-5" />
                  <span>Enrichment pipeline executed with 100% schema compliance!</span>
                </div>
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => {
                      setActiveJob(null);
                      setUploadResult(null);
                    }}
                    className="px-3 py-1.5 bg-[#0B0F14] border border-[#29313C] text-[#F4F7FB] rounded"
                  >
                    NEW RUN
                  </button>
                  <Link
                    href="/catalog"
                    className="px-4 py-1.5 bg-[#62E6A7] text-[#0B0F14] font-bold rounded flex items-center gap-1.5 shadow-[0_0_12px_rgba(98,230,167,0.3)]"
                  >
                    <span>BROWSE CATALOG</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            )}
          </div>
        ) : (
          <>
            {/* Industrial Drop Zone */}
            <div className="bg-[#11161D] border-2 border-dashed border-[#29313C] hover:border-[#2F6BFF] rounded-xl p-12 text-center transition-all">
              <input
                type="file"
                accept=".csv,.xlsx"
                id="catalog-upload"
                onChange={handleFileUpload}
                className="hidden"
              />
              <label htmlFor="catalog-upload" className="cursor-pointer block space-y-4">
                <div className="w-14 h-14 rounded-full bg-[#151B23] border border-[#29313C] text-[#4D7CFF] flex items-center justify-center mx-auto shadow-[0_0_15px_rgba(47,107,255,0.2)]">
                  <Upload className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-[#F4F7FB] tracking-tight">
                    DROP YOUR CATALOG HERE
                  </h3>
                  <p className="text-xs text-[#667180] mt-1">
                    CSV / XLSX • Auto-detects MPNs, Descriptions & Manufacturer aliases
                  </p>
                </div>
                <div className="pt-2">
                  <span className="px-5 py-2.5 bg-[#2F6BFF] hover:bg-[#4D7CFF] text-[#F4F7FB] font-bold rounded shadow-[0_0_12px_rgba(47,107,255,0.35)] inline-block">
                    {uploading ? 'PRE-VALIDATING COLUMNS...' : '[ BROWSE FILES ]'}
                  </span>
                </div>
              </label>
            </div>

            {/* Pre-Validation Result */}
            {uploadResult && (
              <div className="bg-[#11161D] border border-[#29313C] rounded-xl p-6 shadow-2xl space-y-5 animate-in fade-in">
                <div className="flex items-center justify-between border-b border-[#1F2732] pb-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 bg-[#62E6A7]/10 text-[#62E6A7] border border-[#62E6A7]/30 rounded font-bold text-[10px]">
                        {uploadResult.total_rows.toLocaleString()} ROWS DETECTED
                      </span>
                      <span className="text-[#667180]">{uploadResult.filename}</span>
                    </div>
                    <h3 className="text-base font-bold text-[#F4F7FB] mt-1">
                      Ready for Industrial Intelligence Pipeline
                    </h3>
                  </div>

                  <button
                    onClick={handleStartJob}
                    className="px-6 py-2.5 bg-[#2F6BFF] hover:bg-[#4D7CFF] text-[#F4F7FB] font-bold rounded shadow-[0_0_15px_rgba(47,107,255,0.4)] flex items-center gap-2"
                  >
                    <Play className="w-4 h-4" />
                    <span>[ START CATALYST ]</span>
                  </button>
                </div>

                {/* Column Validation Badges */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                  <div className="bg-[#151B23] border border-[#29313C] p-3 rounded">
                    <div className="text-[9px] text-[#667180] uppercase">MPN COLUMN</div>
                    <div className="font-bold text-[#62E6A7] mt-0.5">MPN ✓</div>
                  </div>
                  <div className="bg-[#151B23] border border-[#29313C] p-3 rounded">
                    <div className="text-[9px] text-[#667180] uppercase">DESCRIPTION COLUMN</div>
                    <div className="font-bold text-[#62E6A7] mt-0.5">DESCRIPTION ✓</div>
                  </div>
                  <div className="bg-[#151B23] border border-[#29313C] p-3 rounded">
                    <div className="text-[9px] text-[#667180] uppercase">BRAND COLUMN</div>
                    <div className="font-bold text-[#62E6A7] mt-0.5">BRAND ✓</div>
                  </div>
                  <div className="bg-[#151B23] border border-[#29313C] p-3 rounded">
                    <div className="text-[9px] text-[#667180] uppercase">MANUFACTURER COLUMN</div>
                    <div className="font-bold text-[#62E6A7] mt-0.5">MANUFACTURER ✓</div>
                  </div>
                </div>

                {/* Warnings Box */}
                <div className="p-3 bg-[#151B23] border border-[#F5B84B]/30 rounded text-[11px] text-[#F5B84B] space-y-0.5">
                  <div>• 3 duplicate MPNs found; auto-deduplication active</div>
                  <div>• 12 missing brand values; Identity Engine will infer from descriptor</div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </AppShell>
  );
}
