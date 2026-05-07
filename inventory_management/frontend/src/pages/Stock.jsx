import { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";

export const StockPage = () => {
  const navigate = useNavigate();
  const token = useSelector((state) => state.auth.token);
  const [stocks, setStocks] = useState([]);

  useEffect(() => {
    if (!token) navigate("/login");
    fetch("/api/v1/stock", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then(setStocks);
  }, [token]);

  return (
    <div className="p-12 max-w-7xl mx-auto">
      <h1 className="text-5xl font-bold mb-8">Stock Levels</h1>
      <div className="bg-white rounded-2xl p-8 shadow-xl">
        <table className="min-w-full">
          <thead>
            <tr>
              <th>Product</th>
              <th>Location</th>
              <th>Available</th>
              <th>Reserved</th>
              <th>Free</th>
            </tr>
          </thead>
          <tbody>
            {stocks.map((stock) => (
              <tr key={stock.id}>
                <td>{stock.product_name}</td>
                <td>{stock.location_name}</td>
                <td>{stock.available_qty}</td>
                <td>{stock.reserved_qty}</td>
                <td>{stock.free_qty}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
