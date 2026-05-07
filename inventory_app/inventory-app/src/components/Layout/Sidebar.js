import React from "react";
import { Link, useLocation } from "react-router-dom";
import { LayoutDashboard, Package, Warehouse, ShoppingCart, Truck, Users, FileText, BarChart3, Settings, LogOut, Menu, X, TrendingUp, Boxes } from "lucide-react";
import { useAuth } from "../../contexts/AuthContext";

const Sidebar = ({ isOpen, toggleSidebar }) => {
  const location = useLocation();
  const { logout } = useAuth();

  const menuItems = [
    { path: "/", icon: LayoutDashboard, label: "Dashboard" },
    { path: "/products", icon: Package, label: "Products" },
    { path: "/stock", icon: Boxes, label: "Stock" },
    { path: "/warehouses", icon: Warehouse, label: "Warehouses" },
    { path: "/purchase-orders", icon: ShoppingCart, label: "Purchase Orders" },
    { path: "/sales-orders", icon: Truck, label: "Sales Orders" },
    { path: "/transfers", icon: TrendingUp, label: "Transfers" },
    { path: "/suppliers", icon: Users, label: "Suppliers" },
    { path: "/customers", icon: Users, label: "Customers" },
    { path: "/reports", icon: BarChart3, label: "Reports" },
    { path: "/settings", icon: Settings, label: "Settings" },
  ];

  const isActive = (path) => {
    if (path === "/" && location.pathname === "/") return true;
    if (path !== "/" && location.pathname.startsWith(path)) return true;
    return false;
  };

  return (
    <div className={`fixed left-0 top-0 h-full bg-gray-900 text-white transition-all duration-300 z-20 ${isOpen ? "w-64" : "w-20"}`}>
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        {isOpen && <h1 className="text-xl font-bold">Inventory Pro</h1>}
        <button onClick={toggleSidebar} className="p-1 hover:bg-gray-800 rounded transition-colors">
          {isOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      <nav className="mt-8">
        {menuItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`flex items-center px-4 py-3 transition-colors ${isActive(item.path) ? "bg-blue-600 border-l-4 border-blue-400" : "hover:bg-gray-800"}`}>
            <item.icon size={20} />
            {isOpen && <span className="ml-3">{item.label}</span>}
          </Link>
        ))}
      </nav>

      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-700">
        <button onClick={logout} className="flex items-center w-full px-4 py-2 hover:bg-gray-800 rounded transition-colors">
          <LogOut size={20} />
          {isOpen && <span className="ml-3">Logout</span>}
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
