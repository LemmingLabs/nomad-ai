import { apiClient } from '../../../../shared/api';

interface LoginPayload { email: string; password: string; }
interface AuthResponse { access_token: string; token_type: string; user_id: number; }

export const loginApi = {
  login: (payload: LoginPayload) =>
    apiClient.post<AuthResponse>('/auth/login', payload).then((response) => response.data),
};
