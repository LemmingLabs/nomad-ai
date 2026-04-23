export type AnalyticsMetrics = {
  impressions_count: number
  interactions_count: number
  interactions_by_type: Record<string, number>
}

export type BusinessAnalyticsOverview = AnalyticsMetrics

export type BusinessPlaceAnalytics = AnalyticsMetrics

export type InteractionBreakdownItem = {
  type: string
  count: number
}

