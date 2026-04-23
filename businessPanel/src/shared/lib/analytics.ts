export function calculateCTR(interactionsCount: number, impressionsCount: number) {
  if (!Number.isFinite(interactionsCount) || !Number.isFinite(impressionsCount)) {
    return 0
  }
  if (impressionsCount <= 0) return 0
  return (interactionsCount / impressionsCount) * 100
}

export function formatCTR(value: number) {
  if (!Number.isFinite(value)) return '0%'
  const rounded = Math.round(value * 10) / 10
  return `${rounded}%`
}

export function mapInteractionBreakdownToChartData(
  record: Record<string, number>,
): { type: string; count: number }[] {
  return Object.entries(record)
    .map(([type, count]) => ({ type, count }))
    .filter((item) => Number.isFinite(item.count) && item.count > 0)
    .sort((a, b) => b.count - a.count)
}

