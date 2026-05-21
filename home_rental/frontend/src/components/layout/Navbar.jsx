import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  Menu,
  X,
  Home,
  Map,
  Users,
  MessageSquare,
  FileText,
  BarChart2,
} from "lucide-react";
import useAuthStore from "../../store/useAuthStore";
import toast from "react-hot-toast";
import ThemeToggle from "../ui/ThemeToggle";
import { useEffect } from "react";
import { roommateAPI } from "../../api/roommate";

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const { user, logout } = useAuthStore();
  const [pendingRequests, setPendingRequests] = useState(0);

  useEffect(() => {
    if (!user) return;
    roommateAPI
      .getRequests()
      .then((r) => setPendingRequests(r.data.pending_count || 0))
      .catch(() => {});
  }, [user]);

  const location = useLocation();
  const navigate = useNavigate();

  

  const handleLogout = async () => {
    await logout();
    toast.success("Logged out successfully");
    navigate("/");
  };

  const links = [
    { to: "/", label: "Home", icon: <Home size={15} /> },
    { to: "/search", label: "Rentals", icon: <Home size={15} /> },
    { to: "/map", label: "Map", icon: <Map size={15} /> },
    {
      to: "/roommate/matches",
      label: "Find Roommate",
      icon: <Users size={15} />,
      badge: pendingRequests,
    },
    { to: "/analytics/market", label: "Prices", icon: <BarChart2 size={15} /> },
  ];

  return (
    <nav
      style={{
        position: "sticky",
        top: 0,
        zIndex: 200,
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 2.5rem",
        height: 68,
        background: "var(--bg-primary)",
        borderBottom: "1px solid var(--border)",
        backdropFilter: "blur(16px)",
        WebkitBackdropFilter: "blur(16px)",
        gap: "1rem",
        transition: "background 0.3s ease",
      }}
    >
      {/* Logo */}
      <Link
        to="/"
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          flexShrink: 0,
          textDecoration: "none",
        }}
      >
        <span style={{ fontSize: "1.6rem" }}>🏠</span>
        <span
          style={{
            fontFamily: "'Fraunces', serif",
            fontWeight: 900,
            fontSize: "1.4rem",
            background:
              "linear-gradient(135deg, var(--text-primary), var(--ochre))",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            backgroundClip: "text",
          }}
        >
          NestMate
        </span>
      </Link>

      {/* Desktop Links */}
      <div
        style={{ display: "flex", alignItems: "center", gap: 24 }}
        className="hidden-mobile"
      >
        {links.map((l) => (
          <Link
            key={l.to}
            to={l.to}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              fontSize: "0.88rem",
              fontWeight: location.pathname === l.to ? 700 : 500,
              color:
                location.pathname === l.to
                  ? "var(--ochre)"
                  : "var(--text-secondary)",
              textDecoration: "none",
              transition: "color 0.2s",
            }}
            onMouseEnter={(e) => (e.currentTarget.style.color = "var(--ochre)")}
            onMouseLeave={(e) =>
              (e.currentTarget.style.color =
                location.pathname === l.to
                  ? "var(--ochre)"
                  : "var(--text-secondary)")
            }
          >
            {l.icon} {l.label}
            {l.badge > 0 && (
              <span style={{
                background:   '#dc2626',
                color:        '#fff',
                borderRadius: '50%',
                width:        18,
                height:       18,
                fontSize:     '0.65rem',
                fontWeight:   700,
                display:      'inline-flex',
                alignItems:   'center',
                justifyContent: 'center',
                marginLeft:   2,
              }}>
                {l.badge}
              </span>
            )}
          </Link>
        ))}
      </div>

      {/* Auth + Theme */}
      <div
        style={{ display: "flex", alignItems: "center", gap: 10 }}
        className="hidden-mobile"
      >
        <ThemeToggle />

        {user ? (
          <>
            <Link to="/chat">
              <MessageSquare
                size={20}
                style={{ color: "var(--text-secondary)", cursor: "pointer" }}
              />
            </Link>
            <Link to="/agreements">
              <FileText
                size={20}
                style={{ color: "var(--text-secondary)", cursor: "pointer" }}
              />
            </Link>
           {user?.is_staff && (
                <Link
                  to="/admin-dashboard"
                  style={{
                    fontSize: '0.8rem', fontWeight: 700,
                    background: '#fee2e2', color: '#b91c1c',
                    padding: '4px 12px', borderRadius: 99,
                  }}
                >
                  🛡️ Admin
                </Link>
              )}
            <Link to="/profile">
              <div
                style={{
                  width: 36,
                  height: 36,
                  borderRadius: "50%",
                  background:
                    "linear-gradient(135deg, var(--ochre-bg), var(--ochre-light))",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontWeight: 700,
                  fontSize: "0.9rem",
                  color: "var(--text-primary)",
                  border: "2px solid var(--ochre)",
                  overflow: "hidden",
                  cursor: "pointer",
                }}
              >
                {user.avatar_url ? (
                  <img
                    src={user.avatar_url}
                    alt=""
                    style={{
                      width: "100%",
                      height: "100%",
                      objectFit: "cover",
                    }}
                  />
                ) : (
                  user.username?.[0]?.toUpperCase()
                )}
              </div>
            </Link>
            <button
              onClick={handleLogout}
              style={{
                background: "transparent",
                color: "var(--text-secondary)",
                border: "1.5px solid var(--border)",
                borderRadius: 99,
                padding: "6px 16px",
                fontSize: "0.85rem",
                fontWeight: 600,
                cursor: "pointer",
                transition: "all 0.2s",
              }}
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <Link
              to="/login"
              style={{
                color: "var(--text-primary)",
                fontWeight: 600,
                fontSize: "0.88rem",
                textDecoration: "none",
                padding: "6px 16px",
                borderRadius: 99,
                border: "1.5px solid var(--border)",
              }}
            >
              Login
            </Link>
            <Link
              to="/register"
              style={{
                background: "var(--text-primary)",
                color: "#fff",
                fontWeight: 600,
                fontSize: "0.88rem",
                textDecoration: "none",
                padding: "8px 20px",
                borderRadius: 99,
                transition: "background 0.2s",
              }}
            >
              Join Free
            </Link>
          </>
        )}
      </div>

      {/* Hamburger */}
      <button
        onClick={() => setOpen(!open)}
        className="show-mobile"
        style={{
          background: "none",
          border: "1.5px solid var(--border)",
          borderRadius: 8,
          padding: "6px 10px",
          color: "var(--text-primary)",
          cursor: "pointer",
          display: "none",
        }}
      >
        {open ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Mobile Menu */}
      {open && (
        <div
          style={{
            position: "fixed",
            top: 68,
            left: 0,
            right: 0,
            background: "var(--bg-primary)",
            borderBottom: "1px solid var(--border)",
            padding: "1.5rem 2rem",
            display: "flex",
            flexDirection: "column",
            gap: 16,
            boxShadow: `0 12px 48px var(--shadow-lg)`,
            zIndex: 199,
          }}
        >
          {links.map((l) => (
            <Link
              key={l.to}
              to={l.to}
              onClick={() => setOpen(false)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                color:
                  location.pathname === l.to
                    ? "var(--ochre)"
                    : "var(--text-primary)",
                fontWeight: 500,
                textDecoration: "none",
                fontSize: "0.95rem",
              }}
            >
              {l.icon} {l.label}
            {l.badge > 0 && (
              <span style={{
                background:   '#dc2626',
                color:        '#fff',
                borderRadius: '50%',
                width:        18,
                height:       18,
                fontSize:     '0.65rem',
                fontWeight:   700,
                display:      'inline-flex',
                alignItems:   'center',
                justifyContent: 'center',
                marginLeft:   2,
              }}>
                {l.badge}
              </span>
            )}
            </Link>
          ))}
          <div
            style={{
              borderTop: "1px solid var(--border)",
              paddingTop: 12,
              display: "flex",
              gap: 10,
              alignItems: "center",
            }}
          >
            <ThemeToggle />
            {!user && (
              <>
                <Link
                  to="/login"
                  onClick={() => setOpen(false)}
                  style={{
                    flex: 1,
                    textAlign: "center",
                    padding: "8px",
                    border: "1.5px solid var(--border)",
                    borderRadius: 99,
                    color: "var(--text-primary)",
                    textDecoration: "none",
                    fontWeight: 600,
                    fontSize: "0.9rem",
                  }}
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  onClick={() => setOpen(false)}
                  style={{
                    flex: 1,
                    textAlign: "center",
                    padding: "8px",
                    background: "var(--text-primary)",
                    color: "#fff",
                    borderRadius: 99,
                    textDecoration: "none",
                    fontWeight: 600,
                    fontSize: "0.9rem",
                  }}
                >
                  Join Free
                </Link>
              </>
            )}
            {user && (
              <button
                onClick={handleLogout}
                style={{
                  flex: 1,
                  padding: "8px",
                  border: "1.5px solid var(--border)",
                  borderRadius: 99,
                  background: "none",
                  color: "var(--text-primary)",
                  fontWeight: 600,
                  fontSize: "0.9rem",
                  cursor: "pointer",
                }}
              >
                Logout
              </button>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
