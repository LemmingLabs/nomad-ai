import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Trip, TripListItem } from './types';

interface TripState {
  trips: TripListItem[];
  activeTripId: number | null;
  setTrips: (trips: TripListItem[]) => void;
  setActiveTrip: (id: number | null) => void;
  updateTrip: (trip: Trip) => void;
  addTrip: (trip: TripListItem) => void;
  removeTrip: (id: number) => void;
  clearTrips: () => void;
  activeTrip: () => TripListItem | undefined;
}

export const useTripStore = create<TripState>()(
  persist(
    (set, get) => ({
      trips: [],
      activeTripId: null,
      setTrips: (trips) => set({ trips }),
      setActiveTrip: (activeTripId) => set({ activeTripId }),
      updateTrip: (trip) =>
        set((s) => ({ trips: s.trips.map((t) => (t.id === trip.id ? trip : t)) })),
      addTrip: (trip) =>
        set((s) => ({
          trips: [trip, ...s.trips.filter((existingTrip) => existingTrip.id !== trip.id)],
        })),
      removeTrip: (id) =>
        set((s) => ({
          trips: s.trips.filter((t) => t.id !== id),
          activeTripId: s.activeTripId === id ? null : s.activeTripId,
        })),
      clearTrips: () => set({ trips: [], activeTripId: null }),
      activeTrip: () => {
        const { trips, activeTripId } = get();
        return trips.find((t) => t.id === activeTripId);
      },
    }),
    { name: 'nomad-trips' },
  ),
);
