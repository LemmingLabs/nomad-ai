import { apiClient } from '../../../../shared/api/client'
import type {
  KnowledgeFact,
  KnowledgeFactAudit,
  KnowledgeFactPayload,
  KnowledgeSource,
  KnowledgeSourcePayload,
} from '../model/knowledgeProvenance.types'

export const knowledgeProvenanceApi = {
  async listSources() {
    const { data } = await apiClient.get<KnowledgeSource[]>('/admin/knowledge-sources')
    return data
  },
  async createSource(payload: KnowledgeSourcePayload) {
    const { data } = await apiClient.post<KnowledgeSource>('/admin/knowledge-sources', payload)
    return data
  },
  async updateSource(id: number, payload: Partial<KnowledgeSourcePayload> & { status?: KnowledgeSource['status'] }) {
    const { data } = await apiClient.patch<KnowledgeSource>(`/admin/knowledge-sources/${id}`, payload)
    return data
  },
  async listFacts() {
    const { data } = await apiClient.get<KnowledgeFact[]>('/admin/knowledge-facts')
    return data
  },
  async createFact(payload: KnowledgeFactPayload) {
    const { data } = await apiClient.post<KnowledgeFact>('/admin/knowledge-facts', payload)
    return data
  },
  async updateFact(id: number, payload: Partial<KnowledgeFactPayload> & { status?: KnowledgeFact['status'] }) {
    const { data } = await apiClient.patch<KnowledgeFact>(`/admin/knowledge-facts/${id}`, payload)
    return data
  },
  async getFactAudit(id: number) {
    const { data } = await apiClient.get<KnowledgeFactAudit[]>(`/admin/knowledge-facts/${id}/audit`)
    return data
  },
}
