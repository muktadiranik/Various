import React, { createContext, useState, useEffect, useContext } from "react";
import api from "../api/axios";
import toast from "react-hot-toast";

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      fetchUser();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUser = async () => {
    try {
      const response = await api.get("/users/me");
      setUser(response.data);
    } catch (error) {
      localStorage.removeItem("access_token");
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      // Create URLSearchParams for form data (not JSON)
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      const response = await api.post("/token", formData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      localStorage.setItem("access_token", response.data.access_token);
      await fetchUser();
      toast.success("Login successful!");
      return true;
    } catch (error) {
      // Extract the actual error message
      const errorMsg = error.response?.data?.detail || "Login failed";
      // Handle array of errors (FastAPI validation errors)
      if (Array.isArray(errorMsg)) {
        toast.error(errorMsg[0]?.msg || "Login failed");
      } else if (typeof errorMsg === "object") {
        toast.error(JSON.stringify(errorMsg));
      } else {
        toast.error(errorMsg);
      }
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    setUser(null);
    toast.success("Logged out successfully");
  };

  return <AuthContext.Provider value={{ user, login, logout, loading }}>{children}</AuthContext.Provider>;
};
