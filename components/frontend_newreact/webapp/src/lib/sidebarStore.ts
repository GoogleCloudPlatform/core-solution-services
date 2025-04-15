import { create } from 'zustand';

interface SidebarState {
    isOpen: boolean;
    activePanel: 'history' | 'settings' | null;
    selectedItem: string | null;
    toggle: () => void;
    setActivePanel: (panel: 'history' | 'settings' | null) => void;
    setSelectedItem: (item: string | null) => void;
}

export const useSidebarStore = create<SidebarState>((set) => ({
    isOpen: true,
    activePanel: null,
    selectedItem: null,
    toggle: () => set((state) => ({ isOpen: !state.isOpen })),
    setActivePanel: (panel) => set({ activePanel: panel }),
    setSelectedItem: (item) => set({ selectedItem: item })
}));