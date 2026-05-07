import React, { useState, useEffect } from "react";
import { Plus, Eye, Truck, Search } from "lucide-react";
import api from "../../api/axios";
import Modal from "../../components/Common/Modal";
import toast from "react-hot-toast";

const SalesOrders = () => {
  const [orders, setOrders] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [products, setProducts] = useState([]);
  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [formData, setFormData] = useState({
    customer_id: "",
    warehouse_id: "",
    items: [],
    shipping_address: "",
    notes: "",
  });
  const [currentItem, setCurrentItem] = useState({ product_id: "", quantity: 1, unit_price: 0, discount: 0 });

  useEffect(() => {
    fetchOrders();
    fetchCustomers();
    fetchProducts();
    fetchWarehouses();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await api.get("/sales-orders");
      setOrders(response.data);
    } catch (error) {
      toast.error("Failed to fetch orders");
    } finally {
      setLoading(false);
    }
  };

  const fetchCustomers = async () => {
    try {
      const response = await api.get("/customers");
      setCustomers(response.data);
    } catch (error) {
      console.error("Failed to fetch customers", error);
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await api.get("/products");
      setProducts(response.data);
    } catch (error) {
      console.error("Failed to fetch products", error);
    }
  };

  const fetchWarehouses = async () => {
    try {
      const response = await api.get("/warehouses");
      setWarehouses(response.data);
    } catch (error) {
      console.error("Failed to fetch warehouses", error);
    }
  };

  const addItem = () => {
    if (currentItem.product_id && currentItem.quantity > 0) {
      const product = products.find((p) => p.id === parseInt(currentItem.product_id));
      const total = currentItem.quantity * currentItem.unit_price - currentItem.discount;
      setFormData({
        ...formData,
        items: [
          ...formData.items,
          {
            product_id: parseInt(currentItem.product_id),
            product_name: product?.name,
            quantity: currentItem.quantity,
            unit_price: currentItem.unit_price,
            discount: currentItem.discount,
            total: total,
          },
        ],
      });
      setCurrentItem({ product_id: "", quantity: 1, unit_price: 0, discount: 0 });
    }
  };

  const removeItem = (index) => {
    const newItems = formData.items.filter((_, i) => i !== index);
    setFormData({ ...formData, items: newItems });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (formData.items.length === 0) {
      toast.error("Please add at least one item");
      return;
    }
    try {
      await api.post("/sales-orders", formData);
      toast.success("Sales order created successfully");
      fetchOrders();
      setShowModal(false);
      setFormData({ customer_id: "", warehouse_id: "", items: [], shipping_address: "", notes: "" });
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to create order");
    }
  };

  const dispatchOrder = async (orderId) => {
    if (window.confirm("Dispatch this order?")) {
      try {
        await api.post(`/sales-orders/${orderId}/dispatch`);
        toast.success("Order dispatched successfully");
        fetchOrders();
      } catch (error) {
        toast.error("Failed to dispatch order");
      }
    }
  };

  const viewOrder = async (orderId) => {
    try {
      const response = await api.get(`/sales-orders/${orderId}`);
      setSelectedOrder(response.data);
    } catch (error) {
      toast.error("Failed to fetch order details");
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: "bg-yellow-100 text-yellow-800",
      confirmed: "bg-blue-100 text-blue-800",
      picked: "bg-purple-100 text-purple-800",
      packed: "bg-indigo-100 text-indigo-800",
      shipped: "bg-cyan-100 text-cyan-800",
      delivered: "bg-green-100 text-green-800",
      cancelled: "bg-red-100 text-red-800",
    };
    return colors[status] || "bg-gray-100 text-gray-800";
  };

  const filteredOrders = orders.filter(
    (order) => order.order_number.toLowerCase().includes(searchTerm.toLowerCase()) || order.customer?.name?.toLowerCase().includes(searchTerm.toLowerCase()),
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Sales Orders</h1>
        <button onClick={() => setShowModal(true)} className="flex items-center space-x-2 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors">
          <Plus size={20} />
          <span>Create SO</span>
        </button>
      </div>

      <div className="mb-4">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
          <input
            type="text"
            placeholder="Search orders..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border rounded-lg dark:bg-gray-700 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">SO Number</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Customer</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Total</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {filteredOrders.map((order) => (
                <tr key={order.id} className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">{order.order_number}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{order.customer?.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{new Date(order.order_date).toLocaleDateString()}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(order.status)}`}>{order.status}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">${order.total?.toLocaleString()}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                    <button onClick={() => viewOrder(order.id)} className="text-blue-500 hover:text-blue-700">
                      <Eye size={18} />
                    </button>
                    {order.status === "pending" && (
                      <button onClick={() => dispatchOrder(order.id)} className="text-green-500 hover:text-green-700">
                        <Truck size={18} />
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {filteredOrders.length === 0 && <div className="text-center py-8 text-gray-500">No sales orders found</div>}
      </div>

      {/* Create SO Modal */}
      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Create Sales Order" size="lg">
        <form onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Customer *</label>
                <select value={formData.customer_id} onChange={(e) => setFormData({ ...formData, customer_id: e.target.value })} className="input-field" required>
                  <option value="">Select Customer</option>
                  {customers.map((customer) => (
                    <option key={customer.id} value={customer.id}>
                      {customer.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Warehouse *</label>
                <select value={formData.warehouse_id} onChange={(e) => setFormData({ ...formData, warehouse_id: e.target.value })} className="input-field" required>
                  <option value="">Select Warehouse</option>
                  {warehouses.map((warehouse) => (
                    <option key={warehouse.id} value={warehouse.id}>
                      {warehouse.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Shipping Address *</label>
              <textarea
                value={formData.shipping_address}
                onChange={(e) => setFormData({ ...formData, shipping_address: e.target.value })}
                className="input-field"
                rows="2"
                required
              />
            </div>

            <div className="border rounded-lg p-4 dark:border-gray-700">
              <h3 className="font-semibold mb-3">Items</h3>
              <div className="grid grid-cols-4 gap-2 mb-2">
                <select value={currentItem.product_id} onChange={(e) => setCurrentItem({ ...currentItem, product_id: e.target.value })} className="col-span-1 input-field">
                  <option value="">Select Product</option>
                  {products.map((product) => (
                    <option key={product.id} value={product.id}>
                      {product.name}
                    </option>
                  ))}
                </select>
                <input
                  type="number"
                  placeholder="Qty"
                  value={currentItem.quantity}
                  onChange={(e) => setCurrentItem({ ...currentItem, quantity: parseFloat(e.target.value) })}
                  className="input-field"
                />
                <input
                  type="number"
                  placeholder="Price"
                  value={currentItem.unit_price}
                  onChange={(e) => setCurrentItem({ ...currentItem, unit_price: parseFloat(e.target.value) })}
                  className="input-field"
                />
                <input
                  type="number"
                  placeholder="Discount"
                  value={currentItem.discount}
                  onChange={(e) => setCurrentItem({ ...currentItem, discount: parseFloat(e.target.value) })}
                  className="input-field"
                />
              </div>
              <button type="button" onClick={addItem} className="text-blue-500 text-sm hover:text-blue-700">
                + Add Item
              </button>

              <div className="mt-4 space-y-2">
                {formData.items.map((item, index) => (
                  <div key={index} className="flex justify-between items-center p-2 bg-gray-50 dark:bg-gray-700 rounded">
                    <span className="text-sm">
                      {item.product_name} x {item.quantity} @ ${item.unit_price} - ${item.discount} = ${item.total}
                    </span>
                    <button type="button" onClick={() => removeItem(index)} className="text-red-500 text-sm">
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Notes</label>
              <textarea value={formData.notes} onChange={(e) => setFormData({ ...formData, notes: e.target.value })} className="input-field" rows="2" />
            </div>
          </div>

          <div className="flex justify-end space-x-3 mt-6">
            <button type="button" onClick={() => setShowModal(false)} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              Create Order
            </button>
          </div>
        </form>
      </Modal>

      {/* Order Details Modal */}
      {selectedOrder && (
        <Modal isOpen={true} onClose={() => setSelectedOrder(null)} title={`SO: ${selectedOrder.order_number}`} size="lg">
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Customer</p>
                <p className="font-medium">{selectedOrder.customer?.name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Warehouse</p>
                <p className="font-medium">{selectedOrder.warehouse?.name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Order Date</p>
                <p>{new Date(selectedOrder.order_date).toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Status</p>
                <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(selectedOrder.status)}`}>{selectedOrder.status}</span>
              </div>
              <div className="col-span-2">
                <p className="text-sm text-gray-500">Shipping Address</p>
                <p className="text-sm">{selectedOrder.shipping_address}</p>
              </div>
            </div>

            <div>
              <h3 className="font-semibold mb-2">Items</h3>
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2">Product</th>
                    <th className="text-right py-2">Quantity</th>
                    <th className="text-right py-2">Unit Price</th>
                    <th className="text-right py-2">Discount</th>
                    <th className="text-right py-2">Total</th>
                  </tr>
                </thead>
                <tbody>
                  {selectedOrder.items?.map((item, idx) => (
                    <tr key={idx} className="border-b">
                      <td className="py-2">{item.product?.name}</td>
                      <td className="text-right py-2">{item.quantity}</td>
                      <td className="text-right py-2">${item.unit_price}</td>
                      <td className="text-right py-2">${item.discount || 0}</td>
                      <td className="text-right py-2">${item.total}</td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr className="border-t">
                    <td colSpan="4" className="text-right py-2 font-semibold">
                      Total:
                    </td>
                    <td className="text-right py-2 font-semibold">${selectedOrder.total}</td>
                  </tr>
                </tfoot>
              </table>
            </div>

            {selectedOrder.notes && (
              <div>
                <p className="text-sm text-gray-500">Notes</p>
                <p className="text-sm">{selectedOrder.notes}</p>
              </div>
            )}
          </div>
          <div className="flex justify-end mt-6">
            <button onClick={() => setSelectedOrder(null)} className="btn-secondary">
              Close
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default SalesOrders;
