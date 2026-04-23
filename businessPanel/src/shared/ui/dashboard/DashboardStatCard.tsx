type DashboardStatCardProps = {
  label: string
  value: string | number
  hint?: string
}

export function DashboardStatCard({ label, value, hint }: DashboardStatCardProps) {
  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-4">
      <div className="text-xs text-neutral-500">{label}</div>
      <div className="mt-1 text-lg font-semibold text-neutral-900">{String(value)}</div>
      {hint ? <div className="mt-1 text-xs text-neutral-500">{hint}</div> : null}
    </div>
  )
}

