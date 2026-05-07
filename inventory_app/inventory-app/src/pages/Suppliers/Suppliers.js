import React, { useState, useEffect } from "react";
import { Plus, Edit, Trash2, Mail, Phone, MapPin } from "lucide-react";
import api from "../../api/axios";
import Modal from "../../components/Common/Modal";
import toast from "react-hot-toast";

const Suppliers = () => {
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingSupplier, setEditingSupplier] = useState(null);
  const [formData, setFormData] = useState({
    name: "",
    code: "",
    contact_person: "",
    email: "",
    phone: "",
    address: "",
    tax_number: "",
    payment_terms: 30,
  });

  useEffect(() => {
    fetchSuppliers();
  }, []);

  const fetchSuppliers = async () => {
    try {
      const response = await api.get("/suppliers");
      setSuppliers(response.data);
    } catch (error) {
      toast.error("Failed to fetch suppliers");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingSupplier) {
        await api.put(`/suppliers/${editingSupplier.id}`, formData);
        toast.success("Supplier updated successfully");
      } else {
        await api.post("/suppliers", formData);
        toast.success("Supplier created successfully");
      }
      fetchSuppliers();
      setShowModal(false);
      resetForm();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Operation failed");
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm("Are you sure you want to delete this supplier?")) {
      try {
        await api.delete(`/suppliers/${id}`);
        toast.success("Supplier deleted successfully");
        fetchSuppliers();
      } catch (error) {
        toast.error("Failed to delete supplier");
      }
    }
  };

  const resetForm = () => {
    setFormData({
      name: "",
      code: "",
      contact_person: "",
      email: "",
      phone: "",
      address: "",
      tax_number: "",
      payment_terms: 30,
    });
    setEditingSupplier(null);
  };

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
        <h1 className="text-2xl font-bold">Suppliers</h1>
        <button onClick={() => setShowModal(true)} className="flex items-center space-x-2 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors">
          <Plus size={20} />
          <span>Add Supplier</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {suppliers.map((supplier) => (
          <div key={supplier.id} className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold">{supplier.name}</h3>
                  <p className="text-sm text-gray-500">Code: {supplier.code}</p>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => {
                      setEditingSupplier(supplier);
                      setFormData(supplier);
                      setShowModal(true);
                    }}
                    className="text-blue-500 hover:text-blue-700">
                    <Edit size={18} />
                  </button>
                  <button onClick={() => handleDelete(supplier.id)} className="text-red-500 hover:text-red-700">
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>

              {supplier.contact_person && <p className="text-sm mb-1">Contact: {supplier.contact_person}</p>}

              <div className="space-y-1 mt-3">
                {supplier.email && (
                  <p className="text-sm flex items-center">
                    <Mail size={14} className="mr-2 text-gray-400" />
                    {supplier.email}
                  </p>
                )}
                {supplier.phone && (
                  <p className="text-sm flex items-center">
                    <Phone size={14} className="mr-2 text-gray-400" />
                    {supplier.phone}
                  </p>
                )}
                {supplier.address && (
                  <p className="text-sm flex items-start">
                    <MapPin size={14} className="mr-2 mt-0.5 text-gray-400" />
                    {supplier.address}
                  </p>
                )}
              </div>

              <div className="mt-3 pt-3 border-t dark:border-gray-700">
                <p className="text-xs text-gray-500">Payment Terms: {supplier.payment_terms} days</p>
                {supplier.tax_number && <p className="text-xs text-gray-500">Tax ID: {supplier.tax_number}</p>}
              </div>
            </div>
          </div>
        ))}
      </div>

      {suppliers.length === 0 && <div className="text-center py-12 text-gray-500">No suppliers found</div>}

      {/* Supplier Form Modal */}
      <Modal
        isOpen={showModal}
        onClose={() => {
          setShowModal(false);
          resetForm();
        }}
        title={editingSupplier ? "Edit Supplier" : "Add Supplier"}
        size="lg">
        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Name *</label>
              <input type="text" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} className="input-field" required />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Code *</label>
              <input type="text" value={formData.code} onChange={(e) => setFormData({ ...formData, code: e.target.value })} className="input-field" required />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Contact Person</label>
              <input type="text" value={formData.contact_person} onChange={(e) => setFormData({ ...formData, contact_person: e.target.value })} className="input-field" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Email</label>
              <input type="email" value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} className="input-field" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Phone</label>
              <input type="tel" value={formData.phone} onChange={(e) => setFormData({ ...formData, phone: e.target.value })} className="input-field" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Tax Number</label>
              <input type="text" value={formData.tax_number} onChange={(e) => setFormData({ ...formData, tax_number: e.target.value })} className="input-field" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Payment Terms (days)</label>
              <input type="number" value={formData.payment_terms} onChange={(e) => setFormData({ ...formData, payment_terms: parseInt(e.target.value) })} className="input-field" />
            </div>
            <div className="col-span-2">
              <label className="block text-sm font-medium mb-1">Address</label>
              <textarea value={formData.address} onChange={(e) => setFormData({ ...formData, address: e.target.value })} className="input-field" rows="2" />
            </div>
          </div>
          <div className="flex justify-end space-x-3 mt-6">
            <button
              type="button"
              onClick={() => {
                setShowModal(false);
                resetForm();
              }}
              className="btn-secondary">
              Cancel
            </button>
            <button type="submit" className="btn-primary">
              {editingSupplier ? "Update" : "Create"}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Suppliers;
