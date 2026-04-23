import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { mapInteractionBreakdownToChartData } from '../model/businessAnalytics.utils'

type BusinessAnalyticsInteractionsChartProps = {
  interactionsByType: Record<string, number>
  height?: number
}

export function BusinessAnalyticsInteractionsChart({
  interactionsByType,
  height = 220,
}: BusinessAnalyticsInteractionsChartProps) {
  const data = mapInteractionBreakdownToChartData(interactionsByType)

  if (data.length === 0) {
    return <div className="text-sm text-neutral-600">No interactions yet.</div>
  }

  return (
    <div style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ left: 8, right: 8 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="type" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
          <Tooltip />
          <Bar dataKey="count" fill="#0a0a0a" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

