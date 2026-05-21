import { Outlet, useLocation } from 'react-router-dom'
import Navbar from './Navbar'
import Footer from './Footer'

export default function Layout() {
  const location = useLocation()
  const noFooter = ['/chat', '/map'].some(p => location.pathname.startsWith(p))

  return (
    <div className="min-h-screen flex flex-col bg-cream">
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
      {!noFooter && <Footer />}
    </div>
  )
}