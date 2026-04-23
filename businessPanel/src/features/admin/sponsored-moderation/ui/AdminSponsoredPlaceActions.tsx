import type { AdminSponsoredPlaceDetails } from '../model/adminSponsoredModeration.types'
import {
  useActivateSponsoredPlaceMutation,
  useApproveSponsoredPlaceMutation,
  useDeactivateSponsoredPlaceMutation,
  useRejectSponsoredPlaceMutation,
} from '../model/adminSponsoredModeration.hooks'
import { confirmAction } from '../../../../shared/lib/confirm'

type AdminSponsoredPlaceActionsProps = {
  place: AdminSponsoredPlaceDetails
}

export function AdminSponsoredPlaceActions({ place }: AdminSponsoredPlaceActionsProps) {
  const approveMutation = useApproveSponsoredPlaceMutation()
  const rejectMutation = useRejectSponsoredPlaceMutation()
  const activateMutation = useActivateSponsoredPlaceMutation()
  const deactivateMutation = useDeactivateSponsoredPlaceMutation()

  const isBusy =
    approveMutation.isPending ||
    rejectMutation.isPending ||
    activateMutation.isPending ||
    deactivateMutation.isPending

  const handleApprove = async () => {
    const ok = confirmAction({ title: 'Approve this sponsored place?' })
    if (!ok) return
    await approveMutation.mutateAsync(place.id)
  }

  const handleReject = async () => {
    const ok = confirmAction({
      title: 'Reject this sponsored place?',
      description: 'This will make it unavailable for promotion.',
    })
    if (!ok) return
    await rejectMutation.mutateAsync(place.id)
  }

  const handleActivate = async () => {
    const ok = confirmAction({ title: 'Activate this sponsored place?' })
    if (!ok) return
    await activateMutation.mutateAsync(place.id)
  }

  const handleDeactivate = async () => {
    const ok = confirmAction({ title: 'Deactivate this sponsored place?' })
    if (!ok) return
    await deactivateMutation.mutateAsync(place.id)
  }

  const showApproveReject = !place.is_approved && place.is_active
  const showDeactivate = place.is_approved && place.is_active
  const showActivate = !place.is_active

  return (
    <div className="flex flex-wrap gap-2">
      {showApproveReject ? (
        <>
          <button
            type="button"
            onClick={handleApprove}
            disabled={isBusy}
            className="rounded-md bg-neutral-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-neutral-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {approveMutation.isPending ? 'Approving...' : 'Approve'}
          </button>
          <button
            type="button"
            onClick={handleReject}
            disabled={isBusy}
            className="rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm font-medium text-red-700 hover:bg-neutral-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {rejectMutation.isPending ? 'Rejecting...' : 'Reject'}
          </button>
        </>
      ) : null}

      {showDeactivate ? (
        <button
          type="button"
          onClick={handleDeactivate}
          disabled={isBusy}
          className="rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm font-medium text-red-700 hover:bg-neutral-50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {deactivateMutation.isPending ? 'Deactivating...' : 'Deactivate'}
        </button>
      ) : null}

      {showActivate ? (
        <button
          type="button"
          onClick={handleActivate}
          disabled={isBusy}
          className="rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm font-medium hover:bg-neutral-50 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {activateMutation.isPending ? 'Activating...' : 'Activate'}
        </button>
      ) : null}
    </div>
  )
}
