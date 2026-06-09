interface DataRow {
  siteId: string
  owner: string
  comments: string
  topology: string
  rca: string
  subRca: string
  status: string
  quality: number
}

interface DataTableProps {
  data: DataRow[]
  showDuplicates?: boolean
  showConflicts?: boolean
}

export default function DataTable({ data }: DataTableProps) {
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'open':
        return 'text-orange-400 bg-orange-400/10'
      case 'in progress':
        return 'text-yellow-400 bg-yellow-400/10'
      case 'resolved':
        return 'text-green-400 bg-green-400/10'
      default:
        return 'text-gray-400 bg-gray-400/10'
    }
  }

  const getQualityColor = (quality: number) => {
    if (quality >= 90) return 'text-green-400'
    if (quality >= 85) return 'text-yellow-400'
    return 'text-orange-400'
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-[#0d1117]">
          <tr>
            <th className="text-left px-6 py-5 text-gray-400 font-semibold text-sm uppercase tracking-wide border-b border-[#21262d]">
              <div className="flex items-center gap-2">
                Site ID
                <svg className="w-4 h-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </th>
            <th className="text-left px-6 py-5 text-gray-400 font-semibold text-sm uppercase tracking-wide border-b border-[#21262d]">Owner</th>
            <th className="text-left px-6 py-5 text-gray-400 font-semibold text-sm uppercase tracking-wide border-b border-[#21262d]">Commentaires concaténés</th>
            <th className="text-left px-6 py-5 text-gray-400 font-semibold text-sm uppercase tracking-wide border-b border-[#21262d]">
              <div className="flex items-center gap-2">
                Topologie
                <svg className="w-4 h-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </th>
            <th className="text-left px-6 py-5 text-gray-400 font-semibold text-sm uppercase tracking-wide border-b border-[#21262d]">RCA</th>
            <th className="text-left px-6 py-5 text-gray-400 font-semibold text-sm uppercase tracking-wide border-b border-[#21262d]">SUB_RCA</th>
            <th className="text-left px-6 py-5 text-gray-400 font-semibold text-sm uppercase tracking-wide border-b border-[#21262d]">Status</th>
            <th className="text-left px-6 py-5 text-gray-400 font-semibold text-sm uppercase tracking-wide border-b border-[#21262d]">Qualité</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <tr 
              key={index}
              className="border-b border-[#21262d] hover:bg-[#161b22] transition-colors"
            >
              <td className="px-6 py-5 text-white text-base font-medium">{row.siteId}</td>
              <td className="px-6 py-5 text-gray-300 text-base">{row.owner}</td>
              <td className="px-6 py-5 text-gray-400 text-sm max-w-md truncate">
                {row.comments}
              </td>
              <td className="px-6 py-5 text-gray-300 text-base">{row.topology}</td>
              <td className="px-6 py-5 text-gray-300 text-base">{row.rca}</td>
              <td className="px-6 py-5 text-gray-300 text-base">{row.subRca}</td>
              <td className="px-6 py-5 text-sm font-semibold">
                <span className={`px-4 py-1.5 rounded-full ${getStatusColor(row.status)}`}>
                  {row.status}
                </span>
              </td>
              <td className={`px-6 py-5 text-base font-bold ${getQualityColor(row.quality)}`}>
                {row.quality}%
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {data.length === 0 && (
        <div className="text-center py-20 text-gray-400">
          Aucune donnée à afficher
        </div>
      )}
    </div>
  )
}
