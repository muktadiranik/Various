import { useEffect, useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { warehousesAPI } from "../services/api";
import { fetchProducts } from "../store/productSlice";

export const Warehouses = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const token = useSelector((state) => state.auth.token);
  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({ name: "", location: "", address: "" });
  const [formLoading, setFormLoading] = useState(false);

  useEffect(() => {
    if (!token) {
      navigate("/login");
      return;
    }
    fetchWarehouses();
  }, [token, navigate]);

  const fetchWarehouses = async () => {
    try {
      setLoading(true);
      const data = await warehousesAPI.list();
      setWarehouses(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setFormLoading(true);
    try {
      await warehousesAPI.create(formData);
      setShowForm(false);
      setFormData({ name: "", location: "", address: "" });
      fetchWarehouses();
    } catch (err) {
      setError(err.message);
    }
    setFormLoading(false);
  };

  const handleEdit = async (warehouse) => {
    setEditingId(warehouse.id);
    setFormData({
      name: warehouse.name,
      location: warehouse.location || "",
      address: warehouse.address || "",
    });
    setShowForm(true);
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    setFormLoading(true);
    try {
      await warehousesAPI.update(editingId, formData);
      setShowForm(false);
      setEditingId(null);
      setFormData({ name: "", location: "", address: "" });
      fetchWarehouses();
    } catch (err) {
      setError(err.message);
    }
    setFormLoading(false);
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingId(null);
    setFormData({ name: "", location: "", address: "" });
    setError(null);
  };

  if (loading) return <div className="p-12">Loading warehouses...</div>;
  if (error) return <div className="p-12 text-red-600">Error: {error}</div>;

  return (
    <div className="p-12 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-12">
        <h1 className="text-5xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">Warehouses</h1>
        <button
          onClick={() => setShowForm(true)}
          className="bg-gradient-to-r from-green-500 to-green-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:from-green-600 hover:to-green-700 shadow-lg hover:shadow-xl transition-all duration-300">
          + New Warehouse
        </button>
      </div>

      <div className="bg-white rounded-3xl shadow-2xl overflow-hidden mb-8">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gradient-to-r from-gray-50 to-gray-100">
            <tr>
              <th className="px-12 py-6 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Name</th>
              <th className="px-6 py-6 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Location</th>
              <th className="px-6 py-6 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Address</th>
              <th className="px-6 py-6 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {warehouses.map((warehouse) => (
              <tr key={warehouse.id} className="hover:bg-gray-50 transition duration-200">
                <td className="px-12 py-6 whitespace-nowrap font-semibold text-gray-900">{warehouse.name}</td>
                <td className="px-6 py-6 whitespace-nowrap text-sm text-gray-600">{warehouse.location || "N/A"}</td>
                <td className="px-6 py-6 whitespace-nowrap text-sm text-gray-500">{warehouse.address || "N/A"}</td>
                <td className="px-6 py-6 whitespace-nowrap text-right text-sm font-weight-500">
                  <div className="flex space-x-2 justify-end">
                    <button onClick={() => handleEdit(warehouse)} className="text-blue-600 hover:text-blue-900 p-2 -m-2 rounded-xl hover:bg-blue-50 transition">
                      Edit
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto">
            <div className="p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">{editingId ? "Edit Warehouse" : "New Warehouse"}</h2>
              <form onSubmit={editingId ? handleUpdate : handleCreate} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Name *</label>
                  <input
                    type="text"
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Location</label>
                  <input
                    type="text"
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                    value={formData.location}
                    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Address</label>
                  <input
                    type="text"
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                    value={formData.address}
                    onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  />
                </div>
                <div className="flex space-x-3 pt-4">
                  <button
                    type="submit"
                    disabled={formLoading}
                    className="flex-1 bg-gradient-to-r from-green-500 to-green-600 text-white py-3 px-4 rounded-xl font-semibold hover:from-green-600 hover:to-green-700 transition shadow-lg disabled:opacity-50">
                    {formLoading ? "Saving..." : editingId ? "Update" : "Create"}
                  </button>
                  <button type="button" onClick={handleCancel} className="flex-1 bg-gray-500 text-white py-3 px-4 rounded-xl font-semibold hover:bg-gray-600 transition shadow-lg">
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
