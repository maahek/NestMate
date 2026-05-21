import { Routes, Route } from "react-router-dom";
import { useEffect, useState } from "react";
import Layout from "./components/layout/Layout";
import useAuthStore from "./store/useAuthStore";
import useThemeStore from "./store/useThemeStore";
import Spinner from "./components/ui/Spinner";
// Pages
import Home from "./pages/Home";
import Search from "./pages/Search";
import ListingDetail from "./pages/ListingDetail";
import CreateListing from "./pages/CreateListing";
import MapSearch from "./pages/MapSearch";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Profile from "./pages/Profile";
import RoommateHome from "./pages/RoommateHome";
import RoommateQuestionnaire from "./pages/RoommateQuestionnaire";
import RoommateMatches from "./pages/RoommateMatches";
import ChatList from "./pages/ChatList";
import ChatRoom from "./pages/ChatRoom";
import AgreementList from "./pages/AgreementList";
import CreateAgreement from "./pages/CreateAgreement";
import MarketPrice from "./pages/MarketPrice";
import AdminDashboard from './pages/AdminDashboard'

export default function App() {
  const { fetchProfile } = useAuthStore();
  const { initTheme } = useThemeStore();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    initTheme();
    fetchProfile().finally(() => setReady(true));
  }, []);

  if (!ready) {
    return (
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          minHeight: "100vh",
          background: "var(--bg-primary)",
        }}
      >
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="search" element={<Search />} />
        <Route path="listing/:id" element={<ListingDetail />} />
        <Route path="listing/create" element={<CreateListing />} />
        <Route path="map" element={<MapSearch />} />
        <Route path="login" element={<Login />} />
        <Route path="register" element={<Register />} />
        <Route path="profile" element={<Profile />} />
        <Route path="roommate" element={<RoommateHome />} />
        <Route path="roommate/quiz" element={<RoommateQuestionnaire />} />
        <Route path="roommate/matches" element={<RoommateMatches />} />
        <Route path="chat" element={<ChatList />} />
        <Route path="chat/:roomId" element={<ChatRoom />} />
        <Route path="agreements" element={<AgreementList />} />
        <Route path="agreements/create/:id" element={<CreateAgreement />} />
        <Route path="analytics/market" element={<MarketPrice />} />
        <Route path="admin-dashboard" element={<AdminDashboard />} />
      </Route>
    </Routes>
  );
}
