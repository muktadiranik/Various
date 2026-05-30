// src/components/user/UserSearch.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { searchUsers } from '../../services/authService';
import Modal from '../common/Modal';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner';
import { IoSearch, IoPersonAdd } from 'react-icons/io5';
import toast from 'react-hot-toast';

function UserSearch({ isOpen, onClose, onSelectUser }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);

  const handleSearch = useCallback(async () => {
    if (!searchTerm.trim()) return;
    setSearching(true);
    try {
      const users = await searchUsers(searchTerm);
      setResults(users);
    } catch (error) {
      toast.error('Failed to search users');
    } finally {
      setSearching(false);
    }
  }, [searchTerm]);

  useEffect(() => {
    const delayDebounce = setTimeout(() => {
      if (searchTerm) {
        handleSearch();
      }
    }, 500);
    return () => clearTimeout(delayDebounce);
  }, [searchTerm, handleSearch]);

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Search Users" size="md">
      <div className="mb-4">
        <div className="relative">
          <input
            type="text"
            placeholder="Search by username or email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-[#202225] text-white rounded p-2 pl-10 focus:outline-none focus:ring-2 focus:ring-[#5865f2]"
          />
          <IoSearch className="absolute left-3 top-3 text-[#b9bbbe]" />
        </div>
      </div>

      {searching ? (
        <div className="flex justify-center py-8">
          <LoadingSpinner />
        </div>
      ) : results.length === 0 && searchTerm ? (
        <div className="text-center py-8">
          <p className="text-[#b9bbbe]">No users found</p>
        </div>
      ) : (
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {results.map((user) => (
            <div key={user.id} className="flex items-center justify-between p-3 bg-[#202225] rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 rounded-full bg-[#5865f2] flex items-center justify-center text-white font-bold">
                  {user.username?.[0]?.toUpperCase()}
                </div>
                <div>
                  <p className="text-white font-semibold">{user.username}</p>
                  <p className="text-[#72767d] text-sm">{user.email}</p>
                </div>
              </div>
              <Button
                variant="primary"
                size="sm"
                onClick={() => {
                  onSelectUser?.(user);
                  onClose();
                }}
              >
                <IoPersonAdd className="mr-1" /> Add
              </Button>
            </div>
          ))}
        </div>
      )}
    </Modal>
  );
}

export default UserSearch;