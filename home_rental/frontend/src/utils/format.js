export const formatINR = (amount) =>
  '₹' + Number(amount).toLocaleString('en-IN')

export const formatDate = (dateStr) =>
  new Date(dateStr).toLocaleDateString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric',
  })

export const timeAgo = (dateStr) => {
  const diff = Math.floor((Date.now() - new Date(dateStr)) / 1000)
  if (diff < 60)     return 'Just now'
  if (diff < 3600)   return `${Math.floor(diff / 60)} min ago`
  if (diff < 86400)  return `${Math.floor(diff / 3600)} hr ago`
  return `${Math.floor(diff / 86400)} days ago`
}

export const slugify = (str) =>
  str.toLowerCase().replace(/\s+/g, '-').replace(/[^\w-]/g, '')