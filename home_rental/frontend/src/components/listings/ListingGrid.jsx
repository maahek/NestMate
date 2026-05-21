import ListingCard from './ListingCard'

export default function ListingGrid({ listings, loading, total }) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="card overflow-hidden animate-pulse">
            <div className="h-48 bg-stone-200" />
            <div className="p-4 space-y-3">
              <div className="h-6 bg-stone-200 rounded-lg w-2/3" />
              <div className="h-4 bg-stone-100 rounded-lg w-full" />
              <div className="h-4 bg-stone-100 rounded-lg w-1/2" />
              <div className="h-2 bg-stone-100 rounded-full w-full mt-3" />
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (!listings || listings.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-stone-400">
        <div className="text-6xl mb-4">🔍</div>
        <h3 className="font-display font-bold text-xl text-navy mb-2">
          No listings found
        </h3>
        <p className="text-sm">Try adjusting your filters or search in a different area.</p>
      </div>
    )
  }

  return (
    <div>
      {total != null && (
        <p className="text-sm text-stone-400 mb-4">
          {total} listing{total !== 1 ? 's' : ''} found
        </p>
      )}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {listings.map((l) => (
          <ListingCard key={l.id} listing={l} />
        ))}
      </div>
    </div>
  )
}