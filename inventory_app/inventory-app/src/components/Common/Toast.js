import React from "react";

export default function Toast({ toast, onClose }) {
  if (!toast) return null;
  return (
    <div className="fixed bottom-4 right-4 z-50 rounded border bg-white p-3 shadow" role="status">
      <div className="text-sm font-medium">{toast.title}</div>
      {toast.message ? <div className="text-sm text-gray-600">{toast.message}</div> : null}
      <button className="mt-2 text-xs text-gray-500 hover:text-gray-800" onClick={onClose}>
        Close
      </button>
    </div>
  );
}
