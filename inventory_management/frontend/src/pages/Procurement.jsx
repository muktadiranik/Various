import { useEffect, useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";

import { productsAPI, stockAPI, procurementAPI } from "../services/api.js";

export const Procurement = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const token = useSelector((state) => state.auth.token);
  const [suppliers, setSuppliers] = useState([]);
  const [pos, setPos] = useState([]);
  const [products, setProducts] = useState([]);
  const [stocks, setStocks] = useState([]);

  useEffect(() => {
    if (!token) navigate("/login");
    // Fetch suppliers
    procurementAPI.suppliers().then(setSuppliers);

    // Fetch POs
    procurementAPI.purchaseOrders().then(setPos);

    // Fetch products and stocks for receipt
    productsAPI.products().then(setProducts);
    stockAPI.list().then(setStocks);
  }, [token]);

  const handleReceipt = async (poId) => {
    const receipt = {
      po_id: poId,
      product_id: products[0]?.id || 1, // First product
      stock_id: stocks[0]?.id || 1,
      unit_cost: 10.0,
      received_qty: 50,
      quality_passed: true,
    };

    await fetch("/api/v1/procurement/goods-receipts", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(receipt),
    });
    alert("Stock updated!");
  };

  return (
    <div className="p-12 max-w-7xl mx-auto">
      <h1 className="text-5xl font-bold mb-8">Procurement</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-2xl p-8 shadow-xl">
          <h2 className="text-2xl font-bold mb-6">Purchase Orders</h2>
          <ul>
            {pos.map((po) => (
              <li key={po.id} className="border p-4 rounded-lg mb-4">
                PO#{po.id} - {po.status} - Supplier: {po.supplier_id}
                <button onClick={() => handleReceipt(po.id)} className="ml-4 bg-green-500 text-white px-4 py-1 rounded">
                  Receive Goods
                </button>
              </li>
            ))}
          </ul>
        </div>
        <div className="bg-white rounded-2xl p-8 shadow-xl">
          <h2 className="text-2xl font-bold mb-6">Suppliers</h2>
          <ul>
            {suppliers.map((s) => (
              <li key={s.id}>
                {s.name} - {s.contact_email}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};
