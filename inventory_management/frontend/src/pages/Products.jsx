import { useEffect, useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { fetchProducts, fetchCategories, createProduct, updateProduct } from "../store/productSlice";
import { useNavigate } from "react-router-dom";

export const Products = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { products, categories, loading, formLoading, error } = useSelector((state) => state.products);
  const token = useSelector((state) => state.auth.token);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({ name: "", sku: "", description: "", category_id: "", uom: "pcs", barcode: "", min_stock_level: 0 });

  useEffect(() => {
    if (!token) {
      navigate("/login");
      return;
    }
    dispatch(fetchProducts());
    dispatch(fetchCategories());
  }, [dispatch, token, navigate]);

  const handleCreate = async (e) => {
    e.preventDefault();
    dispatch(createProduct(formData));
    setShowForm(false);
    setFormData({ name: "", sku: "", description: "", category_id: "", uom: "pcs", barcode: "", min_stock_level: 0 });
  };

  const handleEdit = async (product) => {
    setEditingId(product.id);
    setFormData({
      name: product.name,
      sku: product.sku,
      description: product.description || "",
      category_id: product.category_id,
      uom: product.uom || "pcs",
      barcode: product.barcode || "",
      min_stock_level: product.min_stock_level || 0,
    });
    setShowForm(true);
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    dispatch(updateProduct({ id: editingId, data: formData }));
    setShowForm(false);
    setEditingId(null);
    setFormData({ name: "", sku: "", description: "", category_id: "", uom: "pcs", barcode: "", min_stock_level: 0 });
  };

  const handleCancel = () => {
    dispatch({ type: "products/resetFormLoading" });
    setShowForm(false);
    setEditingId(null);
    setFormData({ name: "", sku: "", description: "", category_id: "", uom: "pcs", barcode: "", min_stock_level: 0 });
  };

  if (loading) return <div className="p-12">Loading...</div>;
  if (error) return <div className="p-12 text-red-600">Error: {error}</div>;

  return (
    <div className="p-12 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-12">
        <div>
          <h1 className="text-5xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent mb-2">Products</h1>
          <p className="text-xl text-gray-600">Manage your product catalog</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="bg-gradient-to-r from-green-500 to-green-600 text-white px-8 py-4 rounded-xl font-semibold text-lg hover:from-green-600 hover:to-green-700 shadow-lg hover:shadow-xl transition-all duration-300"
          disabled={formLoading}>
          + New Product
        </button>
      </div>

      <div className="bg-white shadow-2xl rounded-3xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gradient-to-r from-gray-50 to-gray-100">
              <tr>
                <th className="px-12 py-6 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Product</th>
                <th className="px-6 py-6 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">SKU</th>
                <th className="px-6 py-6 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Stock</th>
                <th className="px-6 py-6 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Price</th>
                <th className="px-6 py-6 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Status</th>
                <th className="px-6 py-6 text-right text-xs font-bold text-gray-700 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {products.map((product) => {
                const totalStock = product.stocks ? product.stocks.reduce((sum, stock) => sum + stock.available_qty, 0) : 0;
                const statusClass =
                  totalStock === 0 ? "bg-red-100 text-red-800" : totalStock <= (product.min_stock_level || 0) ? "bg-yellow-100 text-yellow-800" : "bg-green-100 text-green-800";
                const statusText = totalStock === 0 ? "Out of Stock" : totalStock <= (product.min_stock_level || 0) ? "Low Stock" : "In Stock";

                return (
                  <tr key={product.id} className="hover:bg-gray-50 transition duration-200">
                    <td className="px-12 py-6 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-blue-600 rounded-xl flex items-center justify-center mr-4">
                          <span className="text-white font-bold text-sm">{product.sku.slice(0, 3)}</span>
                        </div>
                        <div>
                          <div className="font-semibold text-gray-900">{product.name}</div>
                          <div className="text-sm text-gray-500">{product.sku}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-6 whitespace-nowrap text-sm font-mono bg-gray-100 rounded-lg">{product.sku}</td>
                    <td className="px-6 py-6 whitespace-nowrap">
                      <span className={`inline-flex px-3 py-1 rounded-full text-sm font-semibold ${statusClass}`}>
                        {totalStock} {product.uom}
                      </span>
                    </td>
                    <td className="px-6 py-6 whitespace-nowrap text-sm font-semibold text-gray-900">${product.avg_cost?.toFixed(2) || "N/A"}</td>
                    <td className="px-6 py-6 whitespace-nowrap">
                      <span className={`inline-flex px-3 py-1 rounded-full text-sm font-semibold ${statusClass}`}>{statusText}</span>
                    </td>
                    <td className="px-6 py-6 whitespace-nowrap text-right text-sm font-weight-500">
                      <div className="flex space-x-2 justify-end">
                        <button
                          onClick={() => handleEdit(product)}
                          className="text-blue-600 hover:text-blue-900 p-2 -m-2 rounded-xl hover:bg-blue-50 transition"
                          disabled={formLoading}>
                          Edit
                        </button>
                        <button className="text-indigo-600 hover:text-indigo-900 p-2 -m-2 rounded-xl hover:bg-indigo-50 transition">Stock In</button>
                        <button className="text-orange-600 hover:text-orange-900 p-2 -m-2 rounded-xl hover:bg-orange-50 transition">Movement</button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">{editingId ? "Edit Product" : "New Product"}</h2>
            <form onSubmit={editingId ? handleUpdate : handleCreate} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
                  <label className="block text-sm font-medium text-gray-700 mb-2">SKU *</label>
                  <input
                    type="text"
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                    value={formData.sku}
                    onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
                    required
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                  rows="3"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Category *</label>
                  <select
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                    value={formData.category_id}
                    onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                    required>
                    <option value="">Select category</option>
                    {categories.map((cat) => (
                      <option key={cat.id} value={cat.id}>
                        {cat.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">UOM</label>
                  <input
                    type="text"
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                    value={formData.uom}
                    onChange={(e) => setFormData({ ...formData, uom: e.target.value })}
                  />
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Barcode</label>
                  <input
                    type="text"
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                    value={formData.barcode}
                    onChange={(e) => setFormData({ ...formData, barcode: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Min Stock Level</label>
                  <input
                    type="number"
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                    value={formData.min_stock_level}
                    onChange={(e) => setFormData({ ...formData, min_stock_level: parseInt(e.target.value) || 0 })}
                  />
                </div>
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
      )}
    </div>
  );
};
