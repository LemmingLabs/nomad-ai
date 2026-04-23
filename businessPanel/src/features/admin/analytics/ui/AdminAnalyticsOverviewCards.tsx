import type { AdminAnalyticsMetrics } from '../model/adminAnalytics.types'
import { calculateCTR, formatCTR } from '../model/adminAnalytics.utils'

type StatCardProps = {
  label: string
  value: string
}

function StatCard({ label, value }: StatCardProps) {
  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-4">
      <div className="text-xs text-neutral-500">{label}</div>
      <div className="mt-1 text-lg font-semibold text-neutral-900">{value}</div>
    </div>
  )
}

type AdminAnalyticsOverviewCardsProps = {
  metrics: AdminAnalyticsMetrics
}

export function AdminAnalyticsOverviewCards({ metrics }: AdminAnalyticsOverviewCardsProps) {
  const ctr = calculateCTR(metrics.interactions_count, metrics.impressions_count)

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
      <StatCard label="Impressions" value={String(metrics.impressions_count)} />
      <StatCard label="Interactions" value={String(metrics.interactions_count)} />
      <StatCard label="CTR" value={formatCTR(ctr)} />
    </div>
  )
}

