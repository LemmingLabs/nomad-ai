import { useMutation, useQuery } from '@tanstack/react-query';
import { useQueryClient } from '@tanstack/react-query';
import { Maximize2, Minimize2, PanelRight } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { messageApi, type Message } from '../../entities/message';
import { useMyLimitsQuery, limitQueryKeys } from '../../entities/limit';
import {
  tripApi,
  useTripStore,
  type Trip,
  type TripItinerary,
} from '../../entities/trip';
import { useUserStore } from '../../entities/user';
import { ChatEditLimitNotice, fallbackFreeLimits, getRemaining, getUsageTone, isLimitExceededError } from '../../features/subscription/view-usage';
import { useSidebarStore } from '../../features/ui/open-sidebar';
import { useMediaQuery } from '../../shared/hooks';
import { getErrorMessage, handleApiError } from '../../shared/lib';
import { Button } from '../../shared/ui';
import { ChatPanel } from '../../widgets/chat-panel';
import { ResizableLayout } from '../../widgets/resizable-layout';
import { Sidebar } from '../../widgets/sidebar';
import { TripPreview } from '../../widgets/trip-preview';
import { UpgradeBanner } from '../../widgets/upgrade-banner';
import styles from './TripPage.module.scss';

export function TripPage() {
  const { id } = useParams<{ id: string }>();
  const tripId = Number(id);
  const { trips, setActiveTrip, updateTrip } = useTripStore();
  const { isAuthenticated } = useUserStore();
  const queryClient = useQueryClient();
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
  const [forceEditLimitReached, setForceEditLimitReached] = useState(false);

  const limitsQuery = useMyLimitsQuery();
  const limits = limitsQuery.data ?? (isAuthenticated ? fallbackFreeLimits : null);
  const remainingEdits = limits
    ? getRemaining(limits.chat_edits_used, limits.chat_edit_limit_per_day)
    : null;
  const editsTone = limits
    ? getUsageTone(limits.chat_edits_used, limits.chat_edit_limit_per_day)
    : 'ok';
  const isChatLimitReached =
    Boolean(isAuthenticated) &&
    Boolean(limits) &&
    (forceEditLimitReached || (remainingEdits !== null && remainingEdits <= 0));

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
      setForceEditLimitReached(false);
      void queryClient.invalidateQueries({ queryKey: limitQueryKeys.me() });
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
      if (isLimitExceededError(error)) {
        setForceEditLimitReached(true);
        void queryClient.invalidateQueries({ queryKey: limitQueryKeys.me() });
        return;
      }
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
              isDisabled={!isAuthenticated || tripQuery.isError || isChatLimitReached}
              disabledPlaceholder={
                !isAuthenticated
                  ? 'Sign in to continue this conversation...'
                  : isChatLimitReached
                    ? 'Daily AI edit limit reached — upgrade to continue'
                    : 'Chat is currently unavailable...'
              }
              notice={
                isAuthenticated && limits ? (
                  <ChatEditLimitNotice
                    remaining={remainingEdits ?? 0}
                    limit={limits.chat_edit_limit_per_day}
                    tone={editsTone}
                  />
                ) : null
              }
              disabledMessage={
                !isAuthenticated ? (
                  <>
                    Sign in to continue chatting with the AI and sync this trip.
                  </>
                ) : tripQuery.isError ? (
                  <>{getErrorMessage(tripQuery.error)}</>
                ) : isChatLimitReached ? (
                  <div style={{ paddingTop: 12 }}>
                    <UpgradeBanner
                      title="You've reached your daily AI edit limit"
                      subtitle="Upgrade your plan to keep refining this itinerary today."
                      ctaTo="/pricing"
                      ctaLabel="Upgrade"
                    />
                  </div>
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
              budget={currentTrip?.budget}
              actions={previewActions}
            />
          </div>
        }
      />
    </div>
  );
}
