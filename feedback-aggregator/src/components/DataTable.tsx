export interface DataRow {
  [key: string]: any  // Support dynamic columns
}

interface DataTableProps {
  data: DataRow[]
  showDuplicates?: boolean
  showConflicts?: boolean
  maxRows?: number  // Limiter le nombre de lignes affichées
}

export default function DataTable({ data, maxRows }: DataTableProps) {
  // Limiter les données affichées si maxRows est défini
  const displayData = maxRows ? data.slice(0, maxRows) : data
  
  const getStatusColor = (status: string) => {
    if (!status) return 'text-gray-400 bg-gray-400/10'
    
    const statusLower = String(status).toLowerCase()
    switch (statusLower) {
      case 'open':
      case 'active':
        return 'text-green-400 bg-green-400/10'
      case 'in progress':
      case 'down':
        return 'text-orange-400 bg-orange-400/10'
      case 'resolved':
      case 'closed':
        return 'text-blue-400 bg-blue-400/10'
      default:
        return 'text-gray-400 bg-gray-400/10'
    }
  }
  
  // Get columns from first row
  const columns = displayData.length > 0 ? Object.keys(displayData[0]) : []

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-[#0d1117]">
          <tr>
            {columns.map((col) => (
              <th 
                key={col}
                className="text-left px-6 py-5 text-gray-400 font-semibold text-sm uppercase tracking-wide border-b border-[#21262d] whitespace-nowrap"
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {displayData.map((row, index) => (
            <tr 
              key={index}
              className="border-b border-[#21262d] hover:bg-[#161b22] transition-colors"
            >
              {columns.map((col) => {
                const value = row[col]
                const isStatusLike = col.toLowerCase().includes('status')
                
                return (
                  <td 
                    key={col} 
                    className="px-6 py-5 text-gray-300 text-sm max-w-md"
                  >
                    {isStatusLike && value ? (
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(value)}`}>
                        {String(value)}
                      </span>
                    ) : (
                      <span className={`${col.toLowerCase().includes('codesite') || col.toLowerCase().includes('site') ? 'text-white font-medium' : ''}`}>
                        {value !== null && value !== undefined ? String(value) : '-'}
                      </span>
                    )}
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
      {displayData.length === 0 && (
        <div className="text-center py-20 text-gray-400">
          Aucune donnée à afficher
        </div>
      )}
    </div>
  )
}
