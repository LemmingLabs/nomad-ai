import { type ChangeEvent, useRef } from 'react'

type SponsoredPlaceMediaUploadProps = {
  isUploading?: boolean
  disabled?: boolean
  onUpload: (file: File) => void
}

export function SponsoredPlaceMediaUpload({
  isUploading,
  disabled,
  onUpload,
}: SponsoredPlaceMediaUploadProps) {
  const inputRef = useRef<HTMLInputElement | null>(null)

  const handleChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    onUpload(file)
    event.target.value = ''
  }

  return (
    <div className="flex items-center gap-3">
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        onChange={handleChange}
        disabled={disabled || isUploading}
        className="hidden"
      />

      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        disabled={disabled || isUploading}
        className="rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm font-medium hover:bg-neutral-50 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isUploading ? 'Uploading...' : 'Upload image'}
      </button>

      <span className="text-xs text-neutral-500">JPG, PNG, WEBP</span>
    </div>
  )
}
