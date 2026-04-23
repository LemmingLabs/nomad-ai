import { useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-toastify';
import { limitQueryKeys } from '../../../../entities/limit';
import { subscriptionQueryKeys, useMockPurchaseMutation } from '../../../../entities/subscription';

export function useMockPurchase() {
  const queryClient = useQueryClient();
  const mutation = useMockPurchaseMutation();

  const purchase = (planId: number) => {
    mutation.mutate(
      { plan_id: planId },
      {
        onSuccess: async () => {
          toast.success('Plan updated!');
          await Promise.all([
            queryClient.invalidateQueries({ queryKey: subscriptionQueryKeys.me() }),
            queryClient.invalidateQueries({ queryKey: limitQueryKeys.me() }),
            queryClient.invalidateQueries({ queryKey: subscriptionQueryKeys.plans() }),
          ]);
        },
        onError: () => {
          toast.error('Could not update your plan. Please try again.');
        },
      },
    );
  };

  return { purchase, mutation };
}

