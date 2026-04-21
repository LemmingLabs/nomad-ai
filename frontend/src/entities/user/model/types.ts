export interface User {
  id: number;
  email: string;
  created_at: string;
  full_name?: string | null;
  avatar_url?: string | null;
}

export interface UserStore {
  user: User | null;
  isAuthenticated: boolean;
  setUser: (user: User | null) => void;
}
