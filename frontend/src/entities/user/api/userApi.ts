import { apiClient } from '../../../shared/api';
import type { User } from '../model/types';

export const userApi = {
  /** GET /auth/me — get current authenticated user */
  getMe: () => apiClient.get<User>('/auth/me').then(r => r.data),
};
