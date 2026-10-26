export type KnowledgeSource = {
  id: number
  name: string
  owner: string | null
  source_url: string
  terms_url: string
  license_basis: string
  allowed_use: string
  attribution_text: string
  geographic_scope: string[]
  freshness_days: number
  approval_evidence: string | null
  status: 'pending' | 'approved' | 'rejected' | 'withdrawn'
  approved_by: number | null
  approved_at: string | null
  created_by: number | null
  created_at: string
  updated_at: string
}

export type KnowledgeFact = {
  id: number
  source_id: number
  source_name: string
  source_url: string
  attribution_text: string
  subject_type: 'place' | 'route'
  subject_id: string
  country_code: string
  fact_type: string
  value: string
  source_record_id: string | null
  source_record_url: string | null
  checked_at: string
  freshness_days: number
  status: 'pending' | 'approved' | 'rejected' | 'withdrawn' | 'stale'
  review_notes: string | null
  reviewed_by: number | null
  reviewed_at: string | null
  created_at: string
  updated_at: string
}

export type KnowledgeFactAudit = {
  id: number
  fact_id: number
  actor_id: number | null
  action: string
  note: string | null
  before_state: Record<string, unknown> | null
  after_state: Record<string, unknown>
  created_at: string
}

export type KnowledgeSourcePayload = Pick<KnowledgeSource,
  'name' | 'owner' | 'source_url' | 'terms_url' | 'license_basis' | 'allowed_use' |
  'attribution_text' | 'geographic_scope' | 'freshness_days' | 'approval_evidence'
>

export type KnowledgeFactPayload = Omit<Pick<KnowledgeFact,
  'source_id' | 'subject_type' | 'subject_id' | 'country_code' | 'fact_type' | 'value' |
  'source_record_id' | 'source_record_url' | 'checked_at' | 'freshness_days' | 'review_notes'
>, 'freshness_days'> & { freshness_days: number | null }
