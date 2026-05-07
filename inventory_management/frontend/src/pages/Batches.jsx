import { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";

export const BatchesPage = () => {
  const navigate = useNavigate();
  const token = useSelector((state) => state.auth.token);
  const [batches, setBatches] = useState([]);

  useEffect(() => {
    if (!token) navigate("/login");
    fetch("/api/v1/batches", {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.json())
      .then(setBatches);
  }, [token]);

  return (
    <div className="p-12 max-w-7xl mx-auto">
      <h1 className="text-5xl font-bold mb-8">Batch Management</h1>
      <div className="bg-white rounded-2xl p-8 shadow-xl">
        <table className="min-w-full">
          <thead>
            <tr>
              <th>Batch ID</th>
              <th>Product</th>
              <th>Expiry</th>
              <th>Location</th>
              <th>Qty</th>
            </tr>
          </thead>
          <tbody>
            {batches.map((batch) => (
              <tr key={batch.id}>
                <td>{batch.batch_number}</td>
                <td>{batch.product_name}</td>
                <td>{batch.expiry_date}</td>
                <td>{batch.location_name}</td>
                <td>{batch.quantity}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
