import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState, type FormEvent } from 'react'

import { knowledgeProvenanceApi } from '../../features/admin/knowledge-provenance/api/knowledgeProvenance.api'
import type {
  KnowledgeFact,
  KnowledgeFactPayload,
  KnowledgeSource,
  KnowledgeSourcePayload,
} from '../../features/admin/knowledge-provenance/model/knowledgeProvenance.types'
import { getErrorMessage } from '../../shared/lib/getErrorMessage'
import { PageErrorState } from '../../shared/ui/PageErrorState'
import { PageLoadingState } from '../../shared/ui/PageLoadingState'

const fieldClass = 'mt-1 w-full rounded-md border border-neutral-200 bg-white px-3 py-2 text-sm'
const labelClass = 'block text-sm font-medium text-neutral-700'

const emptySource: KnowledgeSourcePayload = {
  name: '', owner: '', source_url: '', terms_url: '', license_basis: '',
  allowed_use: '', attribution_text: '', geographic_scope: ['KG'],
  freshness_days: 30, approval_evidence: '',
}

const emptyFact: KnowledgeFactPayload = {
  source_id: 0, subject_type: 'place', subject_id: '', country_code: 'KG',
  fact_type: '', value: '', source_record_id: '', source_record_url: '',
  checked_at: new Date().toISOString().slice(0, 16), freshness_days: 30,
  review_notes: '',
}

function Input({ label, ...props }: React.InputHTMLAttributes<HTMLInputElement> & { label: string }) {
  return (
    <label className={labelClass}>
      {label}
      <input className={fieldClass} {...props} />
    </label>
  )
}

function Textarea({ label, ...props }: React.TextareaHTMLAttributes<HTMLTextAreaElement> & { label: string }) {
  return (
    <label className={labelClass}>
      {label}
      <textarea className={fieldClass} rows={3} {...props} />
    </label>
  )
}

export function AdminKnowledgeProvenancePage() {
  const queryClient = useQueryClient()
  const sourcesQuery = useQuery({
    queryKey: ['admin', 'knowledge-sources'],
    queryFn: knowledgeProvenanceApi.listSources,
  })
  const factsQuery = useQuery({
    queryKey: ['admin', 'knowledge-facts'],
    queryFn: knowledgeProvenanceApi.listFacts,
  })
  const [sourceForm, setSourceForm] = useState(emptySource)
  const [factForm, setFactForm] = useState(emptyFact)
  const [auditFactId, setAuditFactId] = useState<number | null>(null)
  const auditQuery = useQuery({
    queryKey: ['admin', 'knowledge-facts', auditFactId, 'audit'],
    queryFn: () => knowledgeProvenanceApi.getFactAudit(auditFactId as number),
    enabled: auditFactId !== null,
  })

  const refresh = async () => {
    await Promise.all([
      queryClient.invalidateQueries({ queryKey: ['admin', 'knowledge-sources'] }),
      queryClient.invalidateQueries({ queryKey: ['admin', 'knowledge-facts'] }),
    ])
  }
  const createSource = useMutation({
    mutationFn: knowledgeProvenanceApi.createSource,
    onSuccess: async () => {
      setSourceForm(emptySource)
      await refresh()
    },
  })
  const updateSource = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: { status: string; approval_evidence: string } }) =>
      knowledgeProvenanceApi.updateSource(id, payload as { status: 'pending' | 'approved' | 'rejected' | 'withdrawn'; approval_evidence: string }),
    onSuccess: refresh,
  })
  const createFact = useMutation({
    mutationFn: knowledgeProvenanceApi.createFact,
    onSuccess: async () => {
      setFactForm({ ...emptyFact, checked_at: new Date().toISOString().slice(0, 16) })
      await refresh()
    },
  })
  const updateFact = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Partial<KnowledgeFactPayload> & { status?: KnowledgeFact['status'] } }) =>
      knowledgeProvenanceApi.updateFact(id, payload),
    onSuccess: refresh,
  })

  if (sourcesQuery.isLoading || factsQuery.isLoading) {
    return <PageLoadingState message="Loading source review records..." />
  }
  if (sourcesQuery.isError || factsQuery.isError) {
    return (
      <PageErrorState
        title="Source provenance"
        message={getErrorMessage(sourcesQuery.error ?? factsQuery.error, 'Failed to load source review records')}
        onRetry={() => { void sourcesQuery.refetch(); void factsQuery.refetch() }}
      />
    )
  }

  const sources = sourcesQuery.data ?? []
  const facts = factsQuery.data ?? []

  const submitSource = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    createSource.mutate({
      ...sourceForm,
      owner: sourceForm.owner || null,
      geographic_scope: sourceForm.geographic_scope.map((code) => code.trim().toUpperCase()).filter(Boolean),
      freshness_days: Number(sourceForm.freshness_days),
      approval_evidence: sourceForm.approval_evidence || null,
    })
  }
  const submitFact = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    createFact.mutate({
      ...factForm,
      source_id: Number(factForm.source_id),
      country_code: factForm.country_code.toUpperCase(),
      checked_at: new Date(factForm.checked_at).toISOString(),
      freshness_days: factForm.freshness_days ? Number(factForm.freshness_days) : null,
      source_record_id: factForm.source_record_id || null,
      source_record_url: factForm.source_record_url || null,
      review_notes: factForm.review_notes || null,
    })
  }

  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-lg font-semibold">Route and place source review</h1>
        <p className="text-sm text-neutral-600">
          Sources and claims begin pending. A source needs recorded terms approval before any fact can be published. No source data is imported automatically.
        </p>
      </header>

      <section className="space-y-4 rounded-lg border border-neutral-200 bg-white p-5">
        <div>
          <h2 className="font-semibold">Register a source</h2>
          <p className="text-xs text-neutral-500">Record the usage basis, allowed use, attribution, geography, and freshness policy before reviewing claims.</p>
        </div>
        <form className="grid gap-3 md:grid-cols-2" onSubmit={submitSource}>
          <Input label="Source name" required value={sourceForm.name} onChange={(event) => setSourceForm({ ...sourceForm, name: event.target.value })} />
          <Input label="Rights holder / owner" value={sourceForm.owner ?? ''} onChange={(event) => setSourceForm({ ...sourceForm, owner: event.target.value })} />
          <Input label="Source URL" type="url" required value={sourceForm.source_url} onChange={(event) => setSourceForm({ ...sourceForm, source_url: event.target.value })} />
          <Input label="Terms URL" type="url" required value={sourceForm.terms_url} onChange={(event) => setSourceForm({ ...sourceForm, terms_url: event.target.value })} />
          <Input label="License / contract basis" required value={sourceForm.license_basis} onChange={(event) => setSourceForm({ ...sourceForm, license_basis: event.target.value })} />
          <Input label="Country codes (comma separated)" required value={sourceForm.geographic_scope.join(', ')} onChange={(event) => setSourceForm({ ...sourceForm, geographic_scope: event.target.value.split(',') })} />
          <Textarea label="Allowed use and restrictions" required value={sourceForm.allowed_use} onChange={(event) => setSourceForm({ ...sourceForm, allowed_use: event.target.value })} />
          <Textarea label="Required attribution text" required value={sourceForm.attribution_text} onChange={(event) => setSourceForm({ ...sourceForm, attribution_text: event.target.value })} />
          <Input label="Freshness period (days)" type="number" min={1} required value={String(sourceForm.freshness_days)} onChange={(event) => setSourceForm({ ...sourceForm, freshness_days: Number(event.target.value) })} />
          <Textarea label="Terms approval evidence / review reference" value={sourceForm.approval_evidence ?? ''} onChange={(event) => setSourceForm({ ...sourceForm, approval_evidence: event.target.value })} />
          <button className="rounded-md bg-neutral-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50" disabled={createSource.isPending} type="submit">Save source as pending</button>
        </form>
        {createSource.isError ? <p className="text-sm text-red-600">{getErrorMessage(createSource.error, 'Could not save source')}</p> : null}

        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead><tr className="border-b text-xs uppercase text-neutral-500"><th className="py-2 pr-3">Source</th><th className="py-2 pr-3">Terms</th><th className="py-2 pr-3">Scope / freshness</th><th className="py-2 pr-3">Evidence and status</th><th className="py-2">Action</th></tr></thead>
            <tbody>{sources.map((source) => (
              <SourceRow key={source.id} source={source} onSave={(statusValue, evidence) => updateSource.mutate({ id: source.id, payload: { status: statusValue, approval_evidence: evidence } })} />
            ))}</tbody>
          </table>
          {sources.length === 0 ? <p className="py-3 text-sm text-neutral-500">No source records yet. Nothing is currently approved for import.</p> : null}
        </div>
      </section>

      <section className="space-y-4 rounded-lg border border-neutral-200 bg-white p-5">
        <div>
          <h2 className="font-semibold">Submit a fact for review</h2>
          <p className="text-xs text-neutral-500">Use a provider record ID for places, or route key `COUNTRY:origin-&gt;destination`. Keep each factual claim separate.</p>
        </div>
        <form className="grid gap-3 md:grid-cols-2" onSubmit={submitFact}>
          <label className={labelClass}>Approved source
            <select className={fieldClass} required value={factForm.source_id || ''} onChange={(event) => setFactForm({ ...factForm, source_id: Number(event.target.value) })}>
              <option value="">Select a source</option>
              {sources.filter((source) => source.status === 'approved').map((source) => <option key={source.id} value={source.id}>{source.name} ({source.geographic_scope.join(', ')})</option>)}
            </select>
          </label>
          <label className={labelClass}>Subject type
            <select className={fieldClass} value={factForm.subject_type} onChange={(event) => setFactForm({ ...factForm, subject_type: event.target.value as KnowledgeFactPayload['subject_type'] })}><option value="place">Place</option><option value="route">Route</option></select>
          </label>
          <Input label="Subject ID" required value={factForm.subject_id} onChange={(event) => setFactForm({ ...factForm, subject_id: event.target.value })} />
          <Input label="Country code" required maxLength={2} value={factForm.country_code} onChange={(event) => setFactForm({ ...factForm, country_code: event.target.value.toUpperCase() })} />
          <Input label="Fact type" required value={factForm.fact_type} onChange={(event) => setFactForm({ ...factForm, fact_type: event.target.value })} />
          <Input label="Source record ID" value={factForm.source_record_id ?? ''} onChange={(event) => setFactForm({ ...factForm, source_record_id: event.target.value })} />
          <Input label="Source record URL" type="url" value={factForm.source_record_url ?? ''} onChange={(event) => setFactForm({ ...factForm, source_record_url: event.target.value })} />
          <Input label="Checked at" type="datetime-local" required value={factForm.checked_at} onChange={(event) => setFactForm({ ...factForm, checked_at: event.target.value })} />
          <Input label="Freshness override (days, optional)" type="number" min={1} value={factForm.freshness_days ?? ''} onChange={(event) => setFactForm({ ...factForm, freshness_days: event.target.value ? Number(event.target.value) : null })} />
          <Textarea label="Fact value" required value={factForm.value} onChange={(event) => setFactForm({ ...factForm, value: event.target.value })} />
          <Textarea label="Review notes" value={factForm.review_notes ?? ''} onChange={(event) => setFactForm({ ...factForm, review_notes: event.target.value })} />
          <button className="rounded-md bg-neutral-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50" disabled={createFact.isPending || sources.every((source) => source.status !== 'approved')} type="submit">Submit pending fact</button>
        </form>
        {createFact.isError ? <p className="text-sm text-red-600">{getErrorMessage(createFact.error, 'Could not submit fact')}</p> : null}

        <div className="space-y-3">
          {facts.map((fact) => (
            <FactRow
              key={fact.id}
              fact={fact}
              onSave={(payload) => updateFact.mutate({ id: fact.id, payload })}
              onAudit={() => setAuditFactId(auditFactId === fact.id ? null : fact.id)}
              audit={auditFactId === fact.id ? auditQuery.data : undefined}
            />
          ))}
          {facts.length === 0 ? <p className="text-sm text-neutral-500">No route or place claims are stored.</p> : null}
          {updateFact.isError || updateSource.isError ? <p className="text-sm text-red-600">{getErrorMessage(updateFact.error ?? updateSource.error, 'Could not update review record')}</p> : null}
        </div>
      </section>
    </div>
  )
}

function SourceRow({ source, onSave }: {
  source: KnowledgeSource
  onSave: (status: KnowledgeSource['status'], evidence: string) => void
}) {
  const [statusValue, setStatusValue] = useState(source.status)
  const [evidence, setEvidence] = useState(source.approval_evidence ?? '')
  return (
    <tr className="border-b align-top">
      <td className="py-3 pr-3"><div className="font-medium">{source.name}</div><a className="text-xs text-teal-700 underline" href={source.source_url} target="_blank" rel="noreferrer">Source</a></td>
      <td className="py-3 pr-3"><a className="text-xs text-teal-700 underline" href={source.terms_url} target="_blank" rel="noreferrer">{source.license_basis}</a><p className="max-w-sm text-xs text-neutral-500">{source.allowed_use}</p></td>
      <td className="py-3 pr-3 text-xs">{source.geographic_scope.join(', ')}<p>{source.freshness_days} days</p></td>
      <td className="min-w-64 py-3 pr-3"><textarea className={fieldClass} rows={2} value={evidence} onChange={(event) => setEvidence(event.target.value)} placeholder="Approval evidence reference" /><select className={fieldClass} value={statusValue} onChange={(event) => setStatusValue(event.target.value as typeof source.status)}>{['pending', 'approved', 'rejected', 'withdrawn'].map((status) => <option key={status}>{status}</option>)}</select></td>
      <td className="py-3"><button type="button" className="rounded border px-3 py-1.5 text-xs" onClick={() => onSave(statusValue, evidence)}>Save</button><p className="text-xs text-neutral-500">{source.status}</p></td>
    </tr>
  )
}

function FactRow({ fact, onSave, onAudit, audit }: {
  fact: KnowledgeFact
  onSave: (payload: Partial<KnowledgeFactPayload> & { status?: KnowledgeFact['status'] }) => void
  onAudit: () => void
  audit?: Awaited<ReturnType<typeof knowledgeProvenanceApi.getFactAudit>>
}) {
  const [value, setValue] = useState(fact.value)
  const [factType, setFactType] = useState(fact.fact_type)
  return (
    <article className="rounded-md border border-neutral-200 p-4">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div><p className="font-medium">{fact.fact_type}: {fact.value}</p><p className="text-xs text-neutral-500">{fact.subject_type} · {fact.subject_id} · {fact.country_code} · {fact.source_name}</p><p className="text-xs text-neutral-500">Checked {new Date(fact.checked_at).toLocaleDateString()} · freshness {fact.freshness_days} days · {fact.status}</p></div>
        <div className="flex gap-2">
          <button type="button" className="rounded border px-3 py-1.5 text-xs" onClick={() => onSave({ status: 'approved' })} disabled={fact.status !== 'pending'}>Approve</button>
          <button type="button" className="rounded border px-3 py-1.5 text-xs" onClick={() => onSave({ status: 'rejected' })}>Reject</button>
          <button type="button" className="rounded border px-3 py-1.5 text-xs" onClick={() => onSave({ status: 'withdrawn' })}>Withdraw</button>
          <button type="button" className="rounded border px-3 py-1.5 text-xs" onClick={onAudit}>Audit</button>
        </div>
      </div>
      <details className="mt-3">
        <summary className="cursor-pointer text-sm text-teal-800">Update fact</summary>
        <div className="mt-2 grid gap-3 md:grid-cols-2">
          <Input label="Fact type" value={factType} onChange={(event) => setFactType(event.target.value)} />
          <Textarea label="Fact value" value={value} onChange={(event) => setValue(event.target.value)} />
          <button type="button" className="rounded border px-3 py-2 text-sm" onClick={() => onSave({ fact_type: factType, value })}>Save changes and return to pending review</button>
        </div>
      </details>
      {audit ? <ol className="mt-3 space-y-1 border-t pt-3 text-xs text-neutral-600">{audit.map((event) => <li key={event.id}>{new Date(event.created_at).toLocaleString()} · {event.action} · {event.note ?? 'No note'}</li>)}</ol> : null}
    </article>
  )
}
