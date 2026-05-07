import { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";

export const SalesPage = () => {
  const navigate = useNavigate();
  const token = useSelector((state) => state.auth.token);
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    if (!token) navigate("/login");
    fetch("/api/v1/sales", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then(setOrders);
  }, [token]);

  const updateStatus = async (orderId, newStatus) => {
    const updatedOrder = { status: newStatus };
    await fetch(`/api/v1/sales/${orderId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(updatedOrder),
    });
    // Refresh orders
    fetch("/api/v1/sales", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then(setOrders);
  };

  return (
    <div className="p-12 max-w-7xl mx-auto">
      <h1 className="text-5xl font-bold mb-8">Sales Orders</h1>
      <div className="bg-white rounded-2xl p-8 shadow-xl">
        <table className="min-w-full">
          <thead>
            <tr>
              <th>ID</th>
              <th>Customer</th>
              <th>Status</th>
              <th>Total</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((order) => (
              <tr key={order.id}>
                <td>{order.id}</td>
                <td>{order.customer_name}</td>
                <td>{order.status}</td>
                <td>${order.total_amount}</td>
                <td>
                  <select onChange={(e) => updateStatus(order.id, e.target.value)} defaultValue={order.status}>
                    <option value="pending">Pending</option>
                    <option value="confirmed">Confirm (Reserve)</option>
                    <option value="shipped">Ship (Deduct)</option>
                    <option value="returned">Return (Restock)</option>
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
