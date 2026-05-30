// src/components/auth/Register.jsx
import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { Link, useNavigate } from 'react-router-dom';
import { register } from '../../store/slices/authSlice';
import Button from '../common/Button';
import toast from 'react-hot-toast';

function Register() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (formData.password !== formData.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    setLoading(true);
    try {
      await dispatch(register(formData)).unwrap();
      toast.success('Registration successful! Please login.');
      navigate('/login');
    } catch (error) {
      toast.error(error.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-[#36393f]">
      <div className="bg-[#2f3136] p-8 rounded-lg shadow-lg w-96">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white">Create Account</h1>
          <p className="text-[#b9bbbe] mt-2">Join the community</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-[#b9bbbe] text-sm font-semibold mb-2">
              Username
            </label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              className="w-full bg-[#202225] text-white rounded p-2 focus:outline-none focus:ring-2 focus:ring-[#5865f2]"
              required
              minLength={2}
              maxLength={32}
            />
          </div>

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

          <div className="mb-4">
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
              minLength={6}
            />
          </div>

          <div className="mb-6">
            <label className="block text-[#b9bbbe] text-sm font-semibold mb-2">
              Confirm Password
            </label>
            <input
              type="password"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              className="w-full bg-[#202225] text-white rounded p-2 focus:outline-none focus:ring-2 focus:ring-[#5865f2]"
              required
            />
          </div>

          <Button type="submit" variant="primary" size="lg" loading={loading} className="w-full">
            Register
          </Button>
        </form>

        <div className="mt-4 text-center">
          <span className="text-[#b9bbbe]">Already have an account? </span>
          <Link to="/login" className="text-[#5865f2] hover:underline">
            Login
          </Link>
        </div>
      </div>
    </div>
  );
}

export default Register;