import toast from 'react-hot-toast'
import { CheckCircle, XCircle, Info, AlertTriangle } from 'lucide-react'

// Custom toast helpers that match NestMate design
export const showToast = {
  success: (msg) => toast.success(msg, {
    icon: <CheckCircle size={18} className="text-green-600" />,
  }),

  error: (msg) => toast.error(msg, {
    icon: <XCircle size={18} className="text-red-500" />,
  }),

  info: (msg) => toast(msg, {
    icon: <Info size={18} className="text-blue-500" />,
    style: { background: '#dbeafe', color: '#1d4ed8' },
  }),

  warning: (msg) => toast(msg, {
    icon: <AlertTriangle size={18} className="text-ochre" />,
    style: { background: '#fef3c7', color: '#92400e' },
  }),

  loading: (msg) => toast.loading(msg),

  dismiss: (id) => toast.dismiss(id),

  promise: (promise, msgs) => toast.promise(promise, {
    loading: msgs.loading || 'Loading...',
    success: msgs.success || 'Done!',
    error:   msgs.error   || 'Something went wrong',
  }),
}

export default showToast