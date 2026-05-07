const API_BASE = "/api/v1";

const apiClient = {
  get: async (endpoint) => {
    const token = localStorage.getItem("token");
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });
    if (!response.ok) throw new Error("API error");
    return response.json();
  },

  post: async (endpoint, data) => {
    const token = localStorage.getItem("token");
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error("API error");
    return response.json();
  },

  put: async (endpoint, data) => {
    const token = localStorage.getItem("token");
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error("API error");
    return response.json();
  },

  delete: async (endpoint) => {
    const token = localStorage.getItem("token");
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    if (!response.ok) throw new Error("API error");
    return response;
  },
};

// Auth APIs (no token required)
export const authAPI = {
  register: async (data) => {
    const response = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error("Register failed");
    return response.json();
  },

  login: async (data) => {
    const response = await fetch(`${API_BASE}/auth/token`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams(data),
    });
    if (!response.ok) throw new Error("Login failed");
    return response.json();
  },
};

export const productsAPI = {
  categories: () => apiClient.get("/products/categories"),
  products: () => apiClient.get("/products"),
  createProduct: (data) => apiClient.post("/products", data),
  updateProduct: (id, data) => apiClient.put(`/products/${id}`, data),
};

export const warehousesAPI = {
  list: () => apiClient.get("/warehouses"),
  create: (data) => apiClient.post("/warehouses/", data),
  update: (id, data) => apiClient.put(`/warehouses/${id}`, data),
};

export const stockAPI = {
  list: () => apiClient.get("/stock"),
  movements: () => apiClient.get("/stock/movements"),
  createStock: (data) => apiClient.post("/stock", data),
  createMovement: (data) => apiClient.post("/stock/movements", data),
};

export const procurementAPI = {
  suppliers: () => apiClient.get("/procurement/suppliers"),
  purchaseOrders: () => apiClient.get("/procurement/purchase-orders"),
  createSupplier: (data) => apiClient.post("/procurement/suppliers", data),
  createPurchaseOrder: (data) => apiClient.post("/procurement/purchase-orders", data),
  createGoodsReceipt: (data) => apiClient.post("/procurement/goods-receipts", data),
};

export const salesAPI = {
  orders: () => apiClient.get("/sales"),
  createOrder: (data) => apiClient.post("/sales", data),
  updateOrder: (id, data) => apiClient.put(`/sales/${id}`, data),
};

export const batchesAPI = {
  list: () => apiClient.get("/batches"),
  createBatch: (data) => apiClient.post("/batches", data),
  updateBatch: (id, data) => apiClient.put(`/batches/${id}`, data),
};

export const reportsAPI = {
  lowStock: () => apiClient.get("/reports/low-stock"),
  movementsSummary: () => apiClient.get("/reports/movements-summary"),
  cogs: () => apiClient.get("/reports/cogs"),
};

export default apiClient;
