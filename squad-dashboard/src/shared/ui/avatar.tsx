interface AvatarProps {
  initials: string
  color: string
  size?: 'sm' | 'md' | 'lg'
}

const sizeMap = { sm: 'w-7 h-7 text-xs', md: 'w-9 h-9 text-sm', lg: 'w-14 h-14 text-lg' }

export function Avatar({ initials, color, size = 'md' }: AvatarProps) {
  return (
    <div
      className={`${sizeMap[size]} rounded-full flex items-center justify-center font-semibold text-white shrink-0`}
      style={{ backgroundColor: color + '33', border: `1.5px solid ${color}66`, color }}
    >
      {initials}
    </div>
  )
}
