import React, { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, MapPin, Box, X } from 'lucide-react';
import api from '../../api/axios';
import Modal from '../../components/Common/Modal';
import toast from 'react-hot-toast';

const Warehouses = () => {
  const [warehouses, setWarehouses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingWarehouse, setEditingWarehouse] = useState(null);
  const [showLocations, setShowLocations] = useState(null);
  const [locations, setLocations] = useState([]);
  const [showLocationModal, setShowLocationModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    code: '',
    address: ''
  });
  const [locationForm, setLocationForm] = useState({
    zone: '',
    rack: '',
    bin: ''
  });

  useEffect(() => {
    fetchWarehouses();
  }, []);

  const fetchWarehouses = async () => {
    try {
      const response = await api.get('/warehouses');
      setWarehouses(response.data);
    } catch (error) {
      toast.error('Failed to fetch warehouses');
    } finally {
      setLoading(false);
    }
  };

  const fetchLocations = async (warehouseId) => {
    try {
      const response = await api.get(`/warehouses/${warehouseId}/locations`);
      setLocations(response.data);
    } catch (error) {
      toast.error('Failed to fetch locations');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingWarehouse) {
        await api.put(`/warehouses/${editingWarehouse.id}`, formData);
        toast.success('Warehouse updated successfully');
      } else {
        await api.post('/warehouses', formData);
        toast.success('Warehouse created successfully');
      }
      fetchWarehouses();
      setShowModal(false);
      resetForm();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Operation failed');
    }
  };

  const handleAddLocation = async () => {
    if (!showLocations) return;
    try {
      await api.post(`/warehouses/${showLocations.id}/locations`, locationForm);
      toast.success('Location added successfully');
      fetchLocations(showLocations.id);
      setShowLocationModal(false);
      setLocationForm({ zone: '', rack: '', bin: '' });
    } catch (error) {
      toast.error('Failed to add location');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this warehouse?')) {
      try {
        await api.delete(`/warehouses/${id}`);
        toast.success('Warehouse deleted successfully');
        fetchWarehouses();
      } catch (error) {
        toast.error('Failed to delete warehouse');
      }
    }
  };

  const resetForm = () => {
    setFormData({ name: '', code: '', address: '' });
    setEditingWarehouse(null);
  };

  const viewLocations = async (warehouse) => {
    setShowLocations(warehouse);
    await fetchLocations(warehouse.id);
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
        <h1 className="text-2xl font-bold">Warehouses</h1>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center space-x-2 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors"
        >
          <Plus size={20} />
          <span>Add Warehouse</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {warehouses.map((warehouse) => (
          <div key={warehouse.id} className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold">{warehouse.name}</h3>
                  <p className="text-sm text-gray-500">Code: {warehouse.code}</p>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => {
                      setEditingWarehouse(warehouse);
                      setFormData(warehouse);
                      setShowModal(true);
                    }}
                    className="text-blue-500 hover:text-blue-700"
                  >
                    <Edit size={18} />
                  </button>
                  <button
                    onClick={() => handleDelete(warehouse.id)}
                    className="text-red-500 hover:text-red-700"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 flex items-start">
                <MapPin size={16} className="mr-1 mt-0.5 flex-shrink-0" />
                {warehouse.address}
              </p>
              <button
                onClick={() => viewLocations(warehouse)}
                className="w-full mt-2 px-4 py-2 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors text-sm"
              >
                <Box size={16} className="inline mr-2" />
                View Locations
              </button>
            </div>
          </div>
        ))}
      </div>

      {warehouses.length === 0 && (
        <div className="text-center py-12 text-gray-500">No warehouses found</div>
      )}

      {/* Warehouse Locations Modal */}
      {showLocations && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center p-4 border-b dark:border-gray-700">
              <h2 className="text-xl font-bold">{showLocations.name} - Locations</h2>
              <button
                onClick={() => setShowLocations(null)}
                className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
              >
                <X size={20} />
              </button>
            </div>
            <div className="p-4">
              <button
                onClick={() => setShowLocationModal(true)}
                className="mb-4 flex items-center space-x-2 bg-blue-500 text-white px-3 py-1.5 rounded-lg hover:bg-blue-600 text-sm"
              >
                <Plus size={16} />
                <span>Add Location</span>
              </button>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {locations.map((location) => (
                  <div key={location.id} className="border rounded-lg p-3 dark:border-gray-700">
                    <p className="font-medium">Zone: {location.zone}</p>
                    <p className="text-sm text-gray-500">Rack: {location.rack}</p>
                    <p className="text-sm text-gray-500">Bin: {location.bin}</p>
                    <p className="text-xs text-gray-400 mt-2">Barcode: {location.barcode}</p>
                  </div>
                ))}
              </div>
              {locations.length === 0 && (
                <div className="text-center py-8 text-gray-500">No locations added yet</div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Add Location Modal */}
      <Modal isOpen={showLocationModal} onClose={() => setShowLocationModal(false)} title="Add Location">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Zone</label>
            <input
              type="text"
              value={locationForm.zone}
              onChange={(e) => setLocationForm({ ...locationForm, zone: e.target.value })}
              className="input-field"
              placeholder="e.g., Zone A"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Rack</label>
            <input
              type="text"
              value={locationForm.rack}
              onChange={(e) => setLocationForm({ ...locationForm, rack: e.target.value })}
              className="input-field"
              placeholder="e.g., Rack 1"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Bin</label>
            <input
              type="text"
              value={locationForm.bin}
              onChange={(e) => setLocationForm({ ...locationForm, bin: e.target.value })}
              className="input-field"
              placeholder="e.g., Bin A"
            />
          </div>
        </div>
        <div className="flex justify-end space-x-3 mt-6">
          <button onClick={() => setShowLocationModal(false)} className="btn-secondary">Cancel</button>
          <button onClick={handleAddLocation} className="btn-primary">Add Location</button>
        </div>
      </Modal>

      {/* Warehouse Form Modal */}
      <Modal isOpen={showModal} onClose={() => { setShowModal(false); resetForm(); }} title={editingWarehouse ? 'Edit Warehouse' : 'Add Warehouse'}>
        <form onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Name *</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="input-field"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Code *</label>
              <input
                type="text"
                value={formData.code}
                onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                className="input-field"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Address</label>
              <textarea
                value={formData.address}
                onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                className="input-field"
                rows="3"
              />
            </div>
          </div>
          <div className="flex justify-end space-x-3 mt-6">
            <button type="button" onClick={() => { setShowModal(false); resetForm(); }} className="btn-secondary">Cancel</button>
            <button type="submit" className="btn-primary">{editingWarehouse ? 'Update' : 'Create'}</button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Warehouses;