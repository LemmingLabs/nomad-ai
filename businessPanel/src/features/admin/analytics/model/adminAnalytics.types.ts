export type AdminAnalyticsMetrics = {
  impressions_count: number
  interactions_count: number
  interactions_by_type: Record<string, number>
}

export type AdminAnalyticsTargetType = 'business' | 'sponsoredPlace'

export type AdminAnalyticsMode = AdminAnalyticsTargetType

export type AdminAnalyticsSelectionItem = {
  id: number
  label: string
  sublabel?: string
}

