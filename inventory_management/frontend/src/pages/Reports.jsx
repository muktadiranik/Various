import { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";

export const Reports = () => {
  const navigate = useNavigate();
  const token = useSelector((state) => state.auth.token);
  const [lowStock, setLowStock] = useState([]);
  const [valuation, setValuation] = useState(null);

  useEffect(() => {
    if (!token) navigate("/login");
    fetch("/api/v1/reports/low-stock", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then(setLowStock);

    fetch("/api/v1/reports/low-stock", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then(setValuation);
  }, [token]);

  return (
    <div className="p-12 max-w-7xl mx-auto">
      <h1 className="text-5xl font-bold mb-8">Reports & Analytics</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-2xl p-8 shadow-xl">
          <h2 className="text-2xl font-bold mb-6">Low Stock Alerts</h2>
          <ul>
            {lowStock.map((item, i) => (
              <li key={i} className="border p-4 rounded-lg mb-4 bg-yellow-50">
                {item.product} ({item.sku}): {item.current_stock}/{item.min_level}
              </li>
            ))}
          </ul>
        </div>
        <div className="bg-white rounded-2xl p-8 shadow-xl">
          <h2 className="text-2xl font-bold mb-6">Stock Valuation</h2>
          {valuation && (
            <div>
              <p>Product ID: {valuation.product_id}</p>
              <p>
                Value: ${valuation?.total_value?.toFixed(2) || "N/A"} ({valuation?.method || "N/A"})
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
