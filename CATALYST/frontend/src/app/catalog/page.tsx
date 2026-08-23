'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  Search,
  Filter,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  ShieldCheck,
  Globe2,
  Boxes,
  RotateCcw,
  ArrowRight
} from 'lucide-react';
import { AppShell } from '@/components/AppShell';
import { StatusBadge } from '@/components/StatusBadge';
import { getCatalog, CatalogListResponse, ProductDetail } from '@/lib/api';

export default function CatalogPage() {
  const [data, setData] = useState<CatalogListResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const [search, setSearch] = useState<string>('');
  const [brand, setBrand] = useState<string>('');
  const [productType, setProductType] = useState<string>('');
  const [qualityBand, setQualityBand] = useState<string>('');
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(25);

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const res = await getCatalog({
        page,
        page_size: pageSize,
        search: search.trim() || undefined,
        brand: brand || undefined,
        product_type: productType || undefined,
        quality_band: qualityBand || undefined,
      });
      setData(res);
    } catch (err) {
      console.error('Failed to load catalog:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, [page, pageSize, brand, productType, qualityBand]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchProducts();
  };

  const handleResetFilters = () => {
    setSearch('');
    setBrand('');
    setProductType('');
    setQualityBand('');
    setPage(1);
  };

  return (
    <AppShell title="CATALOG DATABASE" subtitle="1,000 Verified Industrial Records">
      <div className="space-y-6 max-w-7xl mx-auto">
        {/* Search and Filters Bar */}
        <div className="bg-[#11161D] border border-[#29313C] rounded-xl p-5 shadow-xl space-y-4 font-mono text-xs">
          <form onSubmit={handleSearchSubmit} className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-[#667180] absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search MPN, Brand, Manufacturer, Specifications..."
                className="w-full bg-[#0B0F14] border border-[#29313C] rounded pl-9 pr-3 py-2 text-[#F4F7FB] placeholder:text-[#667180] focus:outline-none focus:border-[#4D7CFF] transition-colors"
              />
            </div>
            <button
              type="submit"
              className="px-5 py-2 bg-[#2F6BFF] hover:bg-[#4D7CFF] text-[#F4F7FB] font-bold rounded shadow-[0_0_12px_rgba(47,107,255,0.3)] transition-colors"
            >
              QUERY DATABASE
            </button>
          </form>

          {/* Filter Dropdowns */}
          <div className="flex flex-wrap items-center gap-3 pt-3 border-t border-[#1F2732]">
            <div className="flex items-center gap-2">
              <span className="text-[#667180]">BRAND:</span>
              <select
                value={brand}
                onChange={(e) => {
                  setBrand(e.target.value);
                  setPage(1);
                }}
                className="bg-[#0B0F14] border border-[#29313C] rounded px-2.5 py-1 text-[#F4F7FB] focus:outline-none focus:border-[#4D7CFF]"
              >
                <option value="">ALL BRANDS</option>
                {data?.filters_meta.brands.map((b) => (
                  <option key={b} value={b}>{b}</option>
                ))}
              </select>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-[#667180]">CATEGORY:</span>
              <select
                value={productType}
                onChange={(e) => {
                  setProductType(e.target.value);
                  setPage(1);
                }}
                className="bg-[#0B0F14] border border-[#29313C] rounded px-2.5 py-1 text-[#F4F7FB] focus:outline-none focus:border-[#4D7CFF] max-w-xs truncate"
              >
                <option value="">ALL CATEGORIES</option>
                {data?.filters_meta.product_types.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-[#667180]">CONFIDENCE:</span>
              <select
                value={qualityBand}
                onChange={(e) => {
                  setQualityBand(e.target.value);
                  setPage(1);
                }}
                className="bg-[#0B0F14] border border-[#29313C] rounded px-2.5 py-1 text-[#F4F7FB] focus:outline-none focus:border-[#4D7CFF]"
              >
                <option value="">ALL SCORES</option>
                <option value="high">HIGH (≥ 0.80)</option>
                <option value="medium">MEDIUM (0.40–0.79)</option>
                <option value="low">LOW (&lt; 0.40)</option>
              </select>
            </div>

            {(brand || productType || qualityBand || search) && (
              <button
                onClick={handleResetFilters}
                className="ml-auto text-[#98A3B3] hover:text-[#F4F7FB] flex items-center gap-1"
              >
                <RotateCcw className="w-3 h-3" />
                <span>RESET</span>
              </button>
            )}
          </div>
        </div>

        {/* Dark Catalog Table */}
        <div className="bg-[#11161D] border border-[#29313C] rounded-xl shadow-2xl overflow-hidden font-mono">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs divide-y divide-[#1F2732]">
              <thead className="bg-[#151B23] text-[#667180] font-bold uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="px-5 py-3">STATUS</th>
                  <th className="px-5 py-3">MPN</th>
                  <th className="px-5 py-3">BRAND / MFG</th>
                  <th className="px-5 py-3">PRODUCT TYPE</th>
                  <th className="px-5 py-3">RAW DESCRIPTOR</th>
                  <th className="px-5 py-3">SOURCES</th>
                  <th className="px-5 py-3 text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#1F2732] text-[#F4F7FB]">
                {loading ? (
                  <tr>
                    <td colSpan={7} className="px-5 py-16 text-center text-[#667180]">
                      <div className="inline-flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full border-2 border-[#2F6BFF] border-t-transparent animate-spin" />
                        <span>Querying Catalog Records...</span>
                      </div>
                    </td>
                  </tr>
                ) : !data?.items.length ? (
                  <tr>
                    <td colSpan={7} className="px-5 py-16 text-center text-[#667180]">
                      No catalog records found matching query parameters.
                    </td>
                  </tr>
                ) : (
                  data.items.map((prod) => {
                    const hasPrimary = prod.sources?.some((s) => s.authority_level === 'PRIMARY');
                    return (
                      <tr
                        key={prod.id}
                        className="hover:bg-[#151B23] transition-colors group cursor-pointer"
                      >
                        <td className="px-5 py-3.5 whitespace-nowrap">
                          <StatusBadge status={prod.identity?.identity_status || 'VERIFIED'} size="sm" />
                        </td>
                        <td className="px-5 py-3.5 whitespace-nowrap">
                          <Link
                            href={`/catalog/${prod.id}`}
                            className="font-bold text-[#4D7CFF] group-hover:underline block"
                          >
                            {prod.identity?.raw_mpn || 'UNKNOWN'}
                          </Link>
                          <span className="text-[10px] text-[#667180] block">
                            Score: {(prod.web_quality_score || 0).toFixed(2)}
                          </span>
                        </td>
                        <td className="px-5 py-3.5">
                          <div className="font-bold text-[#F4F7FB]">{prod.identity?.brand || '—'}</div>
                          <div className="text-[10px] text-[#667180] truncate max-w-xs">
                            {prod.identity?.manufacturer || prod.identity?.brand || '—'}
                          </div>
                        </td>
                        <td className="px-5 py-3.5">
                          <div className="text-[#F4F7FB]">{prod.taxonomy?.product_type || 'General Hardware'}</div>
                          <div className="text-[10px] text-[#667180] truncate max-w-xs">
                            {prod.taxonomy?.classpath || 'Industrial'}
                          </div>
                        </td>
                        <td className="px-5 py-3.5 text-[#98A3B3] max-w-xs truncate" title={prod.raw?.part_desc}>
                          {prod.raw?.part_desc || '—'}
                        </td>
                        <td className="px-5 py-3.5 whitespace-nowrap">
                          {hasPrimary ? (
                            <span className="px-2 py-0.5 bg-[#62E6A7]/10 text-[#62E6A7] border border-[#62E6A7]/30 rounded text-[10px] font-bold inline-flex items-center gap-1">
                              <Globe2 className="w-3 h-3" />
                              Official Tier 1
                            </span>
                          ) : (
                            <span className="px-2 py-0.5 bg-[#151B23] text-[#667180] border border-[#29313C] rounded text-[10px]">
                              Spec Portal
                            </span>
                          )}
                        </td>
                        <td className="px-5 py-3.5 text-right whitespace-nowrap">
                          <Link
                            href={`/catalog/${prod.id}`}
                            className="text-[11px] font-bold text-[#4D7CFF] hover:text-[#F4F7FB] inline-flex items-center gap-1 transition-colors"
                          >
                            <span>View intelligence</span>
                            <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                          </Link>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {data && (
            <div className="px-5 py-3 border-t border-[#1F2732] bg-[#151B23] flex items-center justify-between text-xs text-[#98A3B3]">
              <div>
                SHOWING <span className="text-[#F4F7FB] font-bold">{(page - 1) * pageSize + 1}</span> TO{' '}
                <span className="text-[#F4F7FB] font-bold">{Math.min(page * pageSize, data.total)}</span> OF{' '}
                <span className="text-[#F4F7FB] font-bold">{data.total.toLocaleString()}</span> PRODUCTS
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page <= 1}
                  className="p-1.5 border border-[#29313C] rounded bg-[#0B0F14] hover:bg-[#1B222C] text-[#F4F7FB] disabled:opacity-30 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <span className="font-bold text-[#F4F7FB]">
                  PAGE {data.page} / {data.total_pages}
                </span>
                <button
                  onClick={() => setPage((p) => Math.min(data.total_pages, p + 1))}
                  disabled={page >= data.total_pages}
                  className="p-1.5 border border-[#29313C] rounded bg-[#0B0F14] hover:bg-[#1B222C] text-[#F4F7FB] disabled:opacity-30 disabled:cursor-not-allowed"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
