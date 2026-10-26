import { afterEach, expect, test, vi } from 'vitest'
import { cleanup, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AdminKnowledgeProvenancePage } from '../../src/pages/admin/AdminKnowledgeProvenancePage'
import { knowledgeProvenanceApi } from '../../src/features/admin/knowledge-provenance/api/knowledgeProvenance.api'

vi.mock('../../src/features/admin/knowledge-provenance/api/knowledgeProvenance.api', () => ({
  knowledgeProvenanceApi: {
    listSources: vi.fn(),
    createSource: vi.fn(),
    updateSource: vi.fn(),
    listFacts: vi.fn(),
    createFact: vi.fn(),
    updateFact: vi.fn(),
    getFactAudit: vi.fn(),
  },
}))

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

test('registers a source, approves a claim, and displays its audit record', async () => {
  const user = userEvent.setup()
  let sourceStatus: 'pending' | 'approved' | 'rejected' | 'withdrawn' = 'pending'
  let facts: Awaited<ReturnType<typeof knowledgeProvenanceApi.listFacts>> = []
  const source = {
    id: 1, name: 'Park authority', owner: 'Park authority', source_url: 'https://example.org/data',
    terms_url: 'https://example.org/terms', license_basis: 'Written permission',
    allowed_use: 'Display attributed permit facts', attribution_text: 'Source: Park authority',
    geographic_scope: ['KG'], freshness_days: 30, approval_evidence: 'CASE-123',
    status: sourceStatus, approved_by: null, approved_at: null, created_by: 1,
    created_at: '2026-10-20T10:00:00Z', updated_at: '2026-10-20T10:00:00Z',
  }
  vi.mocked(knowledgeProvenanceApi.listSources).mockImplementation(async () => [{ ...source, status: sourceStatus }])
  vi.mocked(knowledgeProvenanceApi.listFacts).mockImplementation(async () => facts)
  vi.mocked(knowledgeProvenanceApi.createSource).mockResolvedValue(source)
  vi.mocked(knowledgeProvenanceApi.updateSource).mockImplementation(async (_id, payload) => {
    sourceStatus = payload.status ?? 'pending'
    return { ...source, status: sourceStatus }
  })
  vi.mocked(knowledgeProvenanceApi.createFact).mockImplementation(async (payload) => {
    const fact = {
      id: 8, ...payload, source_name: source.name, source_url: source.source_url,
      attribution_text: source.attribution_text, freshness_days: payload.freshness_days ?? 30,
      status: 'pending' as const, reviewed_by: null, reviewed_at: null,
      created_at: '2026-10-20T10:00:00Z', updated_at: '2026-10-20T10:00:00Z',
    }
    facts = [fact]
    return fact
  })
  vi.mocked(knowledgeProvenanceApi.updateFact).mockImplementation(async (_id, payload) => {
    const fact = { ...facts[0], ...payload, status: payload.status ?? facts[0].status }
    facts = [fact]
    return fact
  })
  vi.mocked(knowledgeProvenanceApi.getFactAudit).mockResolvedValue([{
    id: 2, fact_id: 8, actor_id: 1, action: 'approved', note: 'Checked source record',
    before_state: { status: 'pending' }, after_state: { status: 'approved' },
    created_at: '2026-10-20T10:05:00Z',
  }])

  render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <AdminKnowledgeProvenancePage />
    </QueryClientProvider>,
  )

  await screen.findByRole('heading', { name: 'Route and place source review' })
  await user.type(screen.getByLabelText('Source name'), 'Park authority')
  await user.type(screen.getByLabelText('Rights holder / owner'), 'Park authority')
  await user.type(screen.getByLabelText('Source URL'), 'https://example.org/data')
  await user.type(screen.getByLabelText('Terms URL'), 'https://example.org/terms')
  await user.type(screen.getByLabelText('License / contract basis'), 'Written permission')
  await user.clear(screen.getByLabelText('Country codes (comma separated)'))
  await user.type(screen.getByLabelText('Country codes (comma separated)'), 'KG')
  await user.type(screen.getByLabelText('Allowed use and restrictions'), 'Display attributed permit facts')
  await user.type(screen.getByLabelText('Required attribution text'), 'Source: Park authority')
  await user.type(screen.getByLabelText('Terms approval evidence / review reference'), 'CASE-123')
  await user.click(screen.getByRole('button', { name: 'Save source as pending' }))
  await waitFor(() => expect(knowledgeProvenanceApi.createSource).toHaveBeenCalled())

  await user.selectOptions(screen.getByRole('combobox', { name: 'Source status' }), 'approved')
  await user.click(screen.getByRole('button', { name: 'Save' }))
  await waitFor(() => expect(knowledgeProvenanceApi.updateSource).toHaveBeenCalledWith(1, expect.objectContaining({ status: 'approved' })))

  await user.selectOptions(screen.getByRole('combobox', { name: 'Approved source' }), '1')
  await user.type(screen.getByLabelText('Subject ID'), 'KG:bishkek->karakol')
  await user.type(screen.getByLabelText('Fact type'), 'permit_required')
  await user.type(screen.getByLabelText('Source record ID'), 'PERMIT-42')
  await user.type(screen.getByLabelText('Fact value'), 'Permit required.')
  await user.click(screen.getByRole('button', { name: 'Submit pending fact' }))
  await waitFor(() => expect(knowledgeProvenanceApi.createFact).toHaveBeenCalled())
  expect(knowledgeProvenanceApi.createFact.mock.calls[0][0]).toEqual(expect.objectContaining({ source_record_id: 'PERMIT-42' }))

  await user.click(await screen.findByRole('button', { name: 'Approve' }))
  await waitFor(() => expect(knowledgeProvenanceApi.updateFact).toHaveBeenCalled())
  expect(knowledgeProvenanceApi.updateFact.mock.calls[0].slice(0, 2)).toEqual([8, { status: 'approved' }])
  await user.click(screen.getByRole('button', { name: 'Audit' }))
  expect(await screen.findByText(/approved · Checked source record/)).toBeTruthy()
})
