import type { BusinessAnalyticsOverview } from '../model/businessAnalytics.types'
import { calculateCTR, formatCTR } from '../model/businessAnalytics.utils'

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

type BusinessAnalyticsOverviewCardsProps = {
  overview: BusinessAnalyticsOverview
}

export function BusinessAnalyticsOverviewCards({
  overview,
}: BusinessAnalyticsOverviewCardsProps) {
  const ctr = calculateCTR(overview.interactions_count, overview.impressions_count)

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
      <StatCard label="Impressions" value={String(overview.impressions_count)} />
      <StatCard label="Interactions" value={String(overview.interactions_count)} />
      <StatCard label="CTR" value={formatCTR(ctr)} />
    </div>
  )
}

