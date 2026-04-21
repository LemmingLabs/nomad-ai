import { apiClient } from '../../../../shared/api';
import type { User } from '../../../../entities/user';

interface RegisterPayload { email: string; password: string; }

export const registerApi = {
  register: (payload: RegisterPayload) =>
    apiClient.post<User>('/auth/register', payload).then((response) => response.data),
};
