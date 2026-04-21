import { useMutation, useQuery } from '@tanstack/react-query';
import { Maximize2, Minimize2, PanelRight } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { messageApi, type Message } from '../../entities/message';
import {
  tripApi,
  useTripStore,
  type Trip,
  type TripItinerary,
} from '../../entities/trip';
import { useUserStore } from '../../entities/user';
import { useSidebarStore } from '../../features/ui/open-sidebar';
import { useMediaQuery } from '../../shared/hooks';
import { getErrorMessage, handleApiError } from '../../shared/lib';
import { Button } from '../../shared/ui';
import { ChatPanel } from '../../widgets/chat-panel';
import { ResizableLayout } from '../../widgets/resizable-layout';
import { Sidebar } from '../../widgets/sidebar';
import { TripPreview } from '../../widgets/trip-preview';
import styles from './TripPage.module.scss';

export function TripPage() {
  const { id } = useParams<{ id: string }>();
  const tripId = Number(id);
  const { trips, setActiveTrip, updateTrip } = useTripStore();
  const { isAuthenticated } = useUserStore();
  const { isOpen, isCollapsed, setCollapsed } = useSidebarStore();
  const isMobile = useMediaQuery('(max-width: 768px)');
  const localTrip = trips.find((trip) => trip.id === tripId) as
    | Trip
    | undefined;

  const [messages, setMessages] = useState<Message[] | null>(null);
  const [itineraryOverride, setItineraryOverride] =
    useState<TripItinerary | null>(null);
  const [isPreviewExpanded, setIsPreviewExpanded] = useState(false);
  const [collapsedBeforeFocus, setCollapsedBeforeFocus] = useState(false);

  useEffect(() => {
    if (Number.isFinite(tripId)) {
      setActiveTrip(tripId);
    }
  }, [setActiveTrip, tripId]);

  const tripQuery = useQuery({
    queryKey: ['trip', tripId],
    queryFn: async () => {
      const response = await tripApi.getById(tripId);
      updateTrip(response.trip);
      return response;
    },
    enabled: isAuthenticated && Number.isFinite(tripId),
  });

  const currentTrip = tripQuery.data?.trip ?? localTrip;
  const itinerary = itineraryOverride ?? currentTrip?.itinerary_json ?? null;
  const tripTitle = currentTrip?.title;
  const visibleMessages = messages ?? tripQuery.data?.messages.items ?? [];

  const sendMutation = useMutation({
    mutationFn: (content: string) => messageApi.send(tripId, { content }),
    onMutate: (content) => {
      const optimisticId = -Date.now();
      setMessages((prev) => [
        ...(prev ?? tripQuery.data?.messages.items ?? []),
        {
          id: optimisticId,
          trip_id: tripId,
          role: 'user',
          content,
          created_at: new Date().toISOString(),
        },
      ]);
      return { optimisticId };
    },
    onSuccess: (response) => {
      setMessages((prev) => [
        ...(prev ?? tripQuery.data?.messages.items ?? []),
        response.message,
      ]);
      if (response.updated_itinerary) {
        setItineraryOverride(response.updated_itinerary);
        if (currentTrip) {
          updateTrip({
            ...currentTrip,
            itinerary_json: response.updated_itinerary,
          });
        }
      }
    },
    onError: (error, _variables, context) => {
      setMessages((prev) =>
        (prev ?? tripQuery.data?.messages.items ?? []).filter(
          (message) => message.id !== context?.optimisticId,
        ),
      );
      handleApiError(error);
    },
  });

  const togglePreviewExpand = () => {
    setIsPreviewExpanded((currentValue) => {
      const nextValue = !currentValue;

      if (nextValue) {
        setCollapsedBeforeFocus(isCollapsed);
        setCollapsed(true);
      } else {
        setCollapsed(collapsedBeforeFocus);
      }

      return nextValue;
    });
  };

  const previewActions = (
    <Button
      type='button'
      variant='secondary'
      size='sm'
      leftIcon={
        isPreviewExpanded ? <Minimize2 size={14} /> : <Maximize2 size={14} />
      }
      onClick={togglePreviewExpand}
    >
      {isPreviewExpanded ? 'Exit focus' : 'Focus route'}
    </Button>
  );

  return (
    <div className={styles.layout}>
      <Sidebar isOpen={!isMobile || isOpen} />
      <ResizableLayout
        isRightExpanded={isPreviewExpanded}
        left={
          <div className={styles.chatPane}>
            <div className={styles.chatHeader}>
              <div>
                <p className={styles.chatEyebrow}>nomad Ai</p>
                <h2 className={styles.chatTitle}>Refine the route in chat</h2>
              </div>
              <span className={styles.chatBadge}>
                <PanelRight size={14} />
                Live itinerary
              </span>
            </div>

            <ChatPanel
              messages={visibleMessages}
              isLoading={tripQuery.isLoading || sendMutation.isPending}
              isDisabled={!isAuthenticated || tripQuery.isError}
              disabledMessage={
                !isAuthenticated ? (
                  <>
                    Sign in to continue chatting with the AI and sync this trip.
                  </>
                ) : tripQuery.isError ? (
                  <>{getErrorMessage(tripQuery.error)}</>
                ) : undefined
              }
              onSend={(content) => sendMutation.mutate(content)}
            />
            {!isAuthenticated && (
              <p className={styles.authPrompt}>
                <Link to='/auth/login'>Sign in</Link> to continue this guest
                trip.
              </p>
            )}
          </div>
        }
        right={
          <div className={styles.previewPane}>
            <TripPreview
              itinerary={itinerary}
              tripTitle={tripTitle}
              actions={previewActions}
            />
          </div>
        }
      />
    </div>
  );
}
