import { apiClient } from '../../../shared/api';

export type SponsoredInteractionType =
  | 'click'
  | 'open_website'
  | 'open_map'
  | 'call';

type TrackSponsoredInteractionPayload = {
  tripId?: number | null;
  sponsoredPlaceId: number;
  businessId: number;
  interactionType: SponsoredInteractionType;
};

export async function trackSponsoredInteraction({
  tripId,
  sponsoredPlaceId,
  businessId,
  interactionType,
}: TrackSponsoredInteractionPayload): Promise<void> {
  try {
    await apiClient.post('/sponsored/interactions', {
      trip_id: tripId ?? null,
      sponsored_place_id: sponsoredPlaceId,
      business_id: businessId,
      interaction_type: interactionType,
    });
  } catch (error) {
    console.warn('[SponsoredInteraction]', error);
  }
}
