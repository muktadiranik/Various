import { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from "react-router-dom";
import { Login } from "./components/Login";
import { Dashboard } from "./pages/Dashboard";
import { Products } from "./pages/Products";
import { Warehouses } from "./pages/Warehouses";
import { StockPage } from "./pages/Stock";
import { Procurement } from "./pages/Procurement";
import { SalesPage } from "./pages/Sales";
import { BatchesPage } from "./pages/Batches";
import { Reports } from "./pages/Reports";
import { Register } from "./components/Register";

import { useSelector, useDispatch } from "react-redux";
import { logout } from "./store/authSlice";

function AppContent() {
  const token = useSelector((state) => state.auth.token);
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleLogout = () => {
    dispatch(logout());
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <Link to="/" className="text-2xl font-bold text-gray-900">
            Inventory Pro
          </Link>
          <div className="space-x-4">
            <Link to="/" className="text-blue-600 hover:text-blue-800">
              Dashboard
            </Link>
            <Link to="/products" className="text-blue-600 hover:text-blue-800">
              Products
            </Link>
            <Link to="/warehouses" className="text-blue-600 hover:text-blue-800">
              Warehouses
            </Link>
            <Link to="/stock" className="text-blue-600 hover:text-blue-800">
              Stock
            </Link>
            <Link to="/procurement" className="text-blue-600 hover:text-blue-800">
              Procurement
            </Link>
            <Link to="/sales" className="text-blue-600 hover:text-blue-800">
              Sales
            </Link>
            <Link to="/batches" className="text-blue-600 hover:text-blue-800">
              Batches
            </Link>
            <Link to="/reports" className="text-blue-600 hover:text-blue-800">
              Reports
            </Link>
            {token ? (
              <button onClick={handleLogout} className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600">
                Logout
              </button>
            ) : (
              <>
                <Link to="/login" className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                  Login
                </Link>
                <Link to="/register" className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 ml-2">
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/login" element={<Login />} />
        <Route path="/products" element={<Products />} />
        <Route path="/warehouses" element={<Warehouses />} />
        <Route path="/stock" element={<StockPage />} />
        <Route path="/procurement" element={<Procurement />} />
        <Route path="/sales" element={<SalesPage />} />
        <Route path="/batches" element={<BatchesPage />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/register" element={<Register />} />
      </Routes>
    </div>
  );
}

function App() {
  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AppContent />
    </Router>
  );
}

export default App;
