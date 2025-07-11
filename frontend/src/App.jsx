import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import AdminDashboard from './pages/AdminDashboard';
import AgentDashboard from './pages/AgentDashboard';
import CustomerRecord from './pages/CustomerRecord';
import NotFound from './pages/NotFound';
import Unauthorized from './pages/Unauthorized';
import Logout from './pages/Logout';
import Layout from './layout/Layout';

const App = () => {
  const [user, setUser] = useState(null);

  const handleLogin = (mockUser) => {
    setUser(mockUser);
  };

  const handleLogout = () => {
    setUser(null);
  };

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={<Login onLogin={handleLogin} />}
        />
        <Route
          path="/admin"
          element={
            user?.role === 'admin' ? (
              <Layout user={user} onLogout={() => (window.location.href = '/logout')}>
                <AdminDashboard />
              </Layout>
            ) : (
              <Unauthorized />
            )
          }
        />
        <Route
          path="/agent"
          element={
            user?.role === 'agent' ? (
              <Layout user={user} onLogout={() => (window.location.href = '/logout')}>
                <AgentDashboard />
              </Layout>
            ) : (
              <Unauthorized />
            )
          }
        />
        <Route
          path="/records"
          element={
            user?.role === 'agent' ? (
              <Layout user={user} onLogout={() => (window.location.href = '/logout')}>
                <CustomerRecord />
              </Layout>
            ) : (
              <Unauthorized />
            )
          }
        />
        <Route
          path="/logout"
          element={<Logout onLogout={handleLogout} />}
        />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  );
};

export default App;
