'use client';

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import {
  ArrowLeft,
  ShieldCheck,
  Globe,
  ExternalLink,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Copy,
  Check,
  Boxes,
  Layers,
  Sparkles,
  Cpu
} from 'lucide-react';
import { AppShell } from '@/components/AppShell';
import { StatusBadge } from '@/components/StatusBadge';
import { TrustScoreArc } from '@/components/TrustScoreArc';
import { EvidenceDrawer } from '@/components/EvidenceDrawer';
import { getProductDetail, ProductDetail, ProductAttribute } from '@/lib/api';

export default function ProductDetailPage() {
  const params = useParams();
  const productId = params?.productId as string;

  const [product, setProduct] = useState<ProductDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedAttr, setSelectedAttr] = useState<ProductAttribute | null>(null);
  const [isEvidenceOpen, setIsEvidenceOpen] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);

  useEffect(() => {
    async function load() {
      if (!productId) return;
      try {
        const res = await getProductDetail(productId);
        setProduct(res);
      } catch (err) {
        console.error('Failed to load product:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [productId]);

  const handleCopyMPN = () => {
    if (product?.identity?.raw_mpn) {
      navigator.clipboard.writeText(product.identity.raw_mpn);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleInspectAttribute = (attr: ProductAttribute) => {
    setSelectedAttr(attr);
    setIsEvidenceOpen(true);
  };

  if (loading) {
    return (
      <AppShell title="PRODUCT INTELLIGENCE" subtitle="Loading record...">
        <div className="flex items-center justify-center h-64 text-[#667180] font-mono text-xs">
          <div className="flex items-center gap-2">
            <span className="w-3.5 h-3.5 rounded-full border-2 border-[#2F6BFF] border-t-transparent animate-spin" />
            <span>Loading product intelligence records...</span>
          </div>
        </div>
      </AppShell>
    );
  }

  if (!product) {
    return (
      <AppShell title="RECORD NOT FOUND" subtitle="Catalog Database">
        <div className="bg-[#11161D] border border-[#29313C] rounded-xl p-12 text-center max-w-lg mx-auto font-mono">
          <AlertTriangle className="w-10 h-10 text-[#F5B84B] mx-auto mb-3" />
          <h2 className="text-base font-bold text-[#F4F7FB]">RECORD NOT FOUND</h2>
          <p className="text-xs text-[#98A3B3] mt-1 mb-4">
            Could not find catalog record with identifier {productId}.
          </p>
          <Link
            href="/catalog"
            className="px-4 py-2 bg-[#2F6BFF] text-[#F4F7FB] rounded text-xs font-bold"
          >
            RETURN TO CATALOG
          </Link>
        </div>
      </AppShell>
    );
  }

  const attributes = product.enriched_attributes?.length ? product.enriched_attributes : product.attributes;

  return (
    <AppShell title="PRODUCT INTELLIGENCE" subtitle={`Inspection for ${product.identity?.raw_mpn || 'Record'}`}>
      <div className="space-y-6 max-w-7xl mx-auto font-mono">
        {/* Navigation Bar */}
        <div className="flex items-center justify-between">
          <Link
            href="/catalog"
            className="text-xs font-bold text-[#98A3B3] hover:text-[#F4F7FB] flex items-center gap-1.5 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>RETURN TO CATALOG</span>
          </Link>
          <div className="flex items-center gap-2">
            <span className="text-xs text-[#667180]">CANONICAL ID: {product.id}</span>
          </div>
        </div>

        {/* Master Product Header */}
        <div className="bg-[#11161D] border border-[#29313C] rounded-xl p-6 shadow-xl space-y-4">
          <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
            <div className="space-y-2">
              <div className="flex flex-wrap items-center gap-2.5">
                <span className="px-2.5 py-0.5 bg-[#2F6BFF] text-[#F4F7FB] text-xs font-bold rounded">
                  {product.identity?.brand || 'INDUSTRIAL'}
                </span>
                <button
                  onClick={handleCopyMPN}
                  className="text-sm font-bold text-[#4D7CFF] bg-[#151B23] hover:bg-[#1B222C] border border-[#29313C] px-2.5 py-0.5 rounded inline-flex items-center gap-1.5 transition-colors"
                  title="Copy MPN"
                >
                  <span>{product.identity?.raw_mpn || 'UNKNOWN_MPN'}</span>
                  {copied ? <Check className="w-3 h-3 text-[#62E6A7]" /> : <Copy className="w-3 h-3 text-[#4D7CFF]" />}
                </button>
                <StatusBadge status={product.identity?.identity_status || 'VERIFIED'} />
              </div>

              <h1 className="text-xl md:text-2xl font-extrabold text-[#F4F7FB] tracking-tight">
                {product.content?.short_desc || product.raw?.part_desc || 'Industrial Product'}
              </h1>

              <div className="text-xs text-[#98A3B3]">
                RAW DESCRIPTOR:{' '}
                <span className="text-[#F4F7FB] bg-[#0B0F14] px-2 py-0.5 rounded border border-[#29313C]">
                  {product.raw?.part_desc || 'No raw descriptor'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* 3-Column Split: Left (Identity & Taxonomy), Center (Attributes Table), Right (TrustScoreArc & Sources) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Column (3 Cols): Identity & Taxonomy */}
          <div className="lg:col-span-3 space-y-6">
            {/* Identity Card */}
            <div className="bg-[#11161D] border border-[#29313C] rounded-xl p-5 shadow-xl space-y-4">
              <div className="text-[10px] font-bold text-[#4D7CFF] uppercase tracking-wider flex items-center gap-1.5">
                <Boxes className="w-4 h-4" />
                <span>IDENTITY ENGINE</span>
              </div>
              <div className="space-y-3 text-xs">
                <div>
                  <div className="text-[#667180] text-[10px] uppercase">MANUFACTURER</div>
                  <div className="font-bold text-[#F4F7FB]">{product.identity?.manufacturer || product.identity?.brand || '—'}</div>
                </div>
                <div>
                  <div className="text-[#667180] text-[10px] uppercase">BRAND</div>
                  <div className="font-bold text-[#F4F7FB]">{product.identity?.brand || '—'}</div>
                </div>
                <div>
                  <div className="text-[#667180] text-[10px] uppercase">NORMALIZED MPN</div>
                  <div className="font-bold text-[#4D7CFF]">{product.identity?.normalized_mpn || product.identity?.raw_mpn || '—'}</div>
                </div>
                <div>
                  <div className="text-[#667180] text-[10px] uppercase">CONFIDENCE</div>
                  <div className="font-bold text-[#62E6A7]">{((product.identity?.identity_confidence || 1) * 100).toFixed(0)}%</div>
                </div>
              </div>
            </div>

            {/* Taxonomy Card */}
            <div className="bg-[#11161D] border border-[#29313C] rounded-xl p-5 shadow-xl space-y-4">
              <div className="text-[10px] font-bold text-[#62E6A7] uppercase tracking-wider flex items-center gap-1.5">
                <Layers className="w-4 h-4" />
                <span>INDUSTRIAL TAXONOMY</span>
              </div>
              <div className="space-y-3 text-xs">
                <div>
                  <div className="text-[#667180] text-[10px] uppercase">DEPARTMENT</div>
                  <div className="font-bold text-[#F4F7FB]">{product.taxonomy?.department || 'Abrasives'}</div>
                </div>
                <div>
                  <div className="text-[#667180] text-[10px] uppercase">CLASS</div>
                  <div className="font-bold text-[#F4F7FB]">{product.taxonomy?.class_name || 'Sanding Products'}</div>
                </div>
                <div>
                  <div className="text-[#667180] text-[10px] uppercase">PRODUCT TYPE</div>
                  <div className="font-bold text-[#4D7CFF]">{product.taxonomy?.product_type || 'File Sanding Belt'}</div>
                </div>
                <div className="pt-2 border-t border-[#1F2732]">
                  <div className="text-[#667180] text-[10px] uppercase mb-1">CLASSPATH</div>
                  <div className="text-[11px] text-[#98A3B3] bg-[#0B0F14] p-2 rounded border border-[#29313C] leading-tight">
                    {product.taxonomy?.classpath || 'Industrial > Category'}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Center Column (6 Cols): Technical Attributes Table */}
          <div className="lg:col-span-6 bg-[#11161D] border border-[#29313C] rounded-xl shadow-2xl overflow-hidden">
            <div className="px-5 py-4 border-b border-[#29313C] bg-[#151B23] flex items-center justify-between">
              <div>
                <h3 className="text-xs font-bold text-[#F4F7FB] uppercase tracking-wider">
                  TECHNICAL ATTRIBUTES MATRIX
                </h3>
                <p className="text-[11px] text-[#667180] mt-0.5">
                  Standardized dimensions & engineering ratings
                </p>
              </div>
              <span className="text-[10px] font-bold px-2 py-0.5 bg-[#2F6BFF]/10 text-[#4D7CFF] border border-[#2F6BFF]/30 rounded">
                {attributes?.length || 0} TRACKED
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs divide-y divide-[#1F2732]">
                <thead className="bg-[#0B0F14] text-[#667180] text-[10px] uppercase">
                  <tr>
                    <th className="px-4 py-2.5">ATTRIBUTE</th>
                    <th className="px-4 py-2.5">VALUE</th>
                    <th className="px-4 py-2.5">UOM</th>
                    <th className="px-4 py-2.5">STATUS</th>
                    <th className="px-4 py-2.5 text-right">EVIDENCE</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#1F2732]">
                  {attributes?.map((attr, idx) => (
                    <tr key={idx} className="hover:bg-[#151B23] transition-colors">
                      <td className="px-4 py-3 font-bold text-[#F4F7FB]">{attr.label}</td>
                      <td className="px-4 py-3 font-bold text-[#4D7CFF]">
                        {String(attr.normalized_value || attr.value || '—')}
                      </td>
                      <td className="px-4 py-3 text-[#667180]">{attr.uom || '—'}</td>
                      <td className="px-4 py-3">
                        <StatusBadge status={attr.status} size="sm" />
                      </td>
                      <td className="px-4 py-3 text-right">
                        <button
                          onClick={() => handleInspectAttribute(attr)}
                          className="px-2 py-1 bg-[#151B23] hover:bg-[#1B222C] border border-[#29313C] text-[#62E6A7] hover:border-[#62E6A7]/40 rounded text-[11px] font-bold inline-flex items-center gap-1 transition-colors"
                        >
                          <ShieldCheck className="w-3 h-3" />
                          <span>PROOF</span>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Right Column (3 Cols): TrustScoreArc & Sources */}
          <div className="lg:col-span-3 space-y-6">
            <TrustScoreArc score={product.web_quality_score} size={110} />

            {/* Sources List */}
            <div className="bg-[#11161D] border border-[#29313C] rounded-xl p-5 shadow-xl space-y-3">
              <div className="text-[10px] font-bold text-[#4D7CFF] uppercase tracking-wider">
                AUTHORITATIVE SOURCES
              </div>

              {product.sources?.length ? (
                product.sources.map((src, idx) => (
                  <div key={idx} className="p-3 bg-[#151B23] border border-[#29313C] rounded space-y-1.5 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-[#F4F7FB]">{src.domain}</span>
                      <span className="text-[9px] font-bold bg-[#62E6A7]/10 text-[#62E6A7] px-1.5 py-0.2 rounded border border-[#62E6A7]/30">
                        {src.authority_level}
                      </span>
                    </div>
                    <a
                      href={src.url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-[10px] text-[#4D7CFF] hover:underline flex items-center gap-1 truncate block"
                    >
                      <span className="truncate">{src.url}</span>
                      <ExternalLink className="w-2.5 h-2.5 shrink-0" />
                    </a>
                  </div>
                ))
              ) : (
                <div className="text-[11px] text-[#667180] italic p-3 border border-[#29313C] rounded bg-[#151B23]">
                  No live web sources linked.
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Commerce Descriptions Strip */}
        <div className="bg-[#11161D] border border-[#29313C] rounded-xl p-6 shadow-xl space-y-4">
          <div className="text-xs font-bold text-[#F4F7FB] uppercase tracking-wider">
            COMMERCE-READY SYNTHESIZED DESCRIPTIONS
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div className="bg-[#151B23] border border-[#29313C] rounded p-4 space-y-1">
              <div className="text-[10px] text-[#667180] uppercase">SHORT DESCRIPTION</div>
              <div className="text-[#F4F7FB] font-semibold">{product.content?.short_desc || '—'}</div>
            </div>
            <div className="bg-[#151B23] border border-[#29313C] rounded p-4 space-y-1">
              <div className="text-[10px] text-[#667180] uppercase">INVOICING DESCRIPTION (30 CHARS)</div>
              <div className="text-[#4D7CFF] font-bold">{product.content?.invoice_desc || '—'}</div>
            </div>
            <div className="bg-[#151B23] border border-[#29313C] rounded p-4 space-y-1">
              <div className="text-[10px] text-[#667180] uppercase">TECHNICAL LONG DESCRIPTION</div>
              <div className="text-[#98A3B3] leading-relaxed">{product.content?.long_desc || '—'}</div>
            </div>
          </div>
        </div>
      </div>

      <EvidenceDrawer
        attribute={selectedAttr}
        sources={product.sources || []}
        isOpen={isEvidenceOpen}
        onClose={() => setIsEvidenceOpen(false)}
      />
    </AppShell>
  );
}
