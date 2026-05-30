// src/components/auth/Login.jsx
import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { Link, useNavigate } from 'react-router-dom';
import { login } from '../../store/slices/authSlice';
import Button from '../common/Button';
import toast from 'react-hot-toast';

function Login() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await dispatch(login(formData)).unwrap();
      toast.success('Login successful!');
      navigate('/');
    } catch (error) {
      toast.error(error.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-[#36393f]">
      <div className="bg-[#2f3136] p-8 rounded-lg shadow-lg w-96">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white">Welcome Back</h1>
          <p className="text-[#b9bbbe] mt-2">Sign in to continue</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-[#b9bbbe] text-sm font-semibold mb-2">
              Email
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full bg-[#202225] text-white rounded p-2 focus:outline-none focus:ring-2 focus:ring-[#5865f2]"
              required
            />
          </div>

          <div className="mb-6">
            <label className="block text-[#b9bbbe] text-sm font-semibold mb-2">
              Password
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="w-full bg-[#202225] text-white rounded p-2 focus:outline-none focus:ring-2 focus:ring-[#5865f2]"
              required
            />
          </div>

          <Button type="submit" variant="primary" size="lg" loading={loading} className="w-full">
            Login
          </Button>
        </form>

        <div className="mt-4 text-center">
          <span className="text-[#b9bbbe]">Need an account? </span>
          <Link to="/register" className="text-[#5865f2] hover:underline">
            Register
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Login;