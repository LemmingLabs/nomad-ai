import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface SidebarState {
  isOpen: boolean;
  isCollapsed: boolean;
  toggle: () => void;
  toggleCollapsed: () => void;
  open: () => void;
  close: () => void;
  setCollapsed: (isCollapsed: boolean) => void;
}

export const useSidebarStore = create<SidebarState>()(
  persist(
    (set) => ({
      isOpen: true,
      isCollapsed: false,
      toggle: () => set((state) => ({ isOpen: !state.isOpen })),
      toggleCollapsed: () =>
        set((state) => ({ isCollapsed: !state.isCollapsed })),
      open: () => set({ isOpen: true }),
      close: () => set({ isOpen: false }),
      setCollapsed: (isCollapsed) => set({ isCollapsed }),
    }),
    {
      name: 'nomad-sidebar',
      partialize: (state) => ({ isCollapsed: state.isCollapsed }),
    },
  ),
);
