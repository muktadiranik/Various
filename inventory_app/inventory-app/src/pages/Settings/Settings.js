import React, { useState } from "react";
import { Save, RefreshCw, Database, Bell, Shield, Globe, Palette } from "lucide-react";
import { useTheme } from "../../contexts/ThemeContext";
import toast from "react-hot-toast";

const Settings = () => {
  const { darkMode, setDarkMode } = useTheme();
  const [generalSettings, setGeneralSettings] = useState({
    companyName: "Inventory Pro",
    currency: "USD",
    timezone: "UTC",
    language: "en",
  });
  const [notificationSettings, setNotificationSettings] = useState({
    lowStockAlerts: true,
    orderUpdates: true,
    emailNotifications: true,
    smsNotifications: false,
  });
  const [loading, setLoading] = useState(false);

  const handleGeneralSave = () => {
    setLoading(true);
    setTimeout(() => {
      localStorage.setItem("companySettings", JSON.stringify(generalSettings));
      toast.success("General settings saved");
      setLoading(false);
    }, 500);
  };

  const handleNotificationSave = () => {
    setLoading(true);
    setTimeout(() => {
      localStorage.setItem("notificationSettings", JSON.stringify(notificationSettings));
      toast.success("Notification settings saved");
      setLoading(false);
    }, 500);
  };

  const handleBackup = () => {
    const data = {
      settings: generalSettings,
      notifications: notificationSettings,
      exportedAt: new Date().toISOString(),
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `inventory_backup_${new Date().toISOString().split("T")[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success("Backup created successfully");
  };

  const handleRestore = () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".json";
    input.onchange = (e) => {
      const file = e.target.files[0];
      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          const data = JSON.parse(event.target.result);
          if (data.settings) setGeneralSettings(data.settings);
          if (data.notifications) setNotificationSettings(data.notifications);
          toast.success("Settings restored successfully");
        } catch (error) {
          toast.error("Invalid backup file");
        }
      };
      reader.readAsText(file);
    };
    input.click();
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Settings</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* General Settings */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md">
          <div className="p-4 border-b dark:border-gray-700">
            <h2 className="text-lg font-semibold flex items-center">
              <Globe size={20} className="mr-2" />
              General Settings
            </h2>
          </div>
          <div className="p-4 space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">Company Name</label>
              <input
                type="text"
                value={generalSettings.companyName}
                onChange={(e) => setGeneralSettings({ ...generalSettings, companyName: e.target.value })}
                className="input-field"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Currency</label>
              <select value={generalSettings.currency} onChange={(e) => setGeneralSettings({ ...generalSettings, currency: e.target.value })} className="input-field">
                <option value="USD">USD ($)</option>
                <option value="EUR">EUR (€)</option>
                <option value="GBP">GBP (£)</option>
                <option value="JPY">JPY (¥)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Timezone</label>
              <select value={generalSettings.timezone} onChange={(e) => setGeneralSettings({ ...generalSettings, timezone: e.target.value })} className="input-field">
                <option value="UTC">UTC</option>
                <option value="EST">Eastern Time</option>
                <option value="CST">Central Time</option>
                <option value="PST">Pacific Time</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Language</label>
              <select value={generalSettings.language} onChange={(e) => setGeneralSettings({ ...generalSettings, language: e.target.value })} className="input-field">
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
                <option value="de">German</option>
              </select>
            </div>
            <button onClick={handleGeneralSave} disabled={loading} className="btn-primary w-full flex items-center justify-center">
              <Save size={18} className="mr-2" />
              Save Settings
            </button>
          </div>
        </div>

        {/* Appearance Settings */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md">
          <div className="p-4 border-b dark:border-gray-700">
            <h2 className="text-lg font-semibold flex items-center">
              <Palette size={20} className="mr-2" />
              Appearance
            </h2>
          </div>
          <div className="p-4 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Dark Mode</p>
                <p className="text-sm text-gray-500">Switch between light and dark theme</p>
              </div>
              <button
                onClick={() => setDarkMode(!darkMode)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${darkMode ? "bg-blue-500" : "bg-gray-300"}`}>
                <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${darkMode ? "translate-x-6" : "translate-x-1"}`} />
              </button>
            </div>
          </div>
        </div>

        {/* Notification Settings */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md">
          <div className="p-4 border-b dark:border-gray-700">
            <h2 className="text-lg font-semibold flex items-center">
              <Bell size={20} className="mr-2" />
              Notifications
            </h2>
          </div>
          <div className="p-4 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Low Stock Alerts</p>
                <p className="text-sm text-gray-500">Get notified when stock is low</p>
              </div>
              <label className="relative inline-flex cursor-pointer">
                <input
                  type="checkbox"
                  checked={notificationSettings.lowStockAlerts}
                  onChange={(e) => setNotificationSettings({ ...notificationSettings, lowStockAlerts: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-300 peer-focus:outline-none rounded-full peer peer-checked:bg-blue-500 peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all"></div>
              </label>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">Order Updates</p>
                <p className="text-sm text-gray-500">Get notified about order status changes</p>
              </div>
              <label className="relative inline-flex cursor-pointer">
                <input
                  type="checkbox"
                  checked={notificationSettings.orderUpdates}
                  onChange={(e) => setNotificationSettings({ ...notificationSettings, orderUpdates: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-300 peer-focus:outline-none rounded-full peer peer-checked:bg-blue-500 peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all"></div>
              </label>
            </div>
            <button onClick={handleNotificationSave} disabled={loading} className="btn-primary w-full flex items-center justify-center mt-4">
              <Save size={18} className="mr-2" />
              Save Notification Settings
            </button>
          </div>
        </div>

        {/* Data Management */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md">
          <div className="p-4 border-b dark:border-gray-700">
            <h2 className="text-lg font-semibold flex items-center">
              <Database size={20} className="mr-2" />
              Data Management
            </h2>
          </div>
          <div className="p-4 space-y-3">
            <button
              onClick={handleBackup}
              className="w-full flex items-center justify-center space-x-2 px-4 py-2 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
              <Database size={18} />
              <span>Export Backup</span>
            </button>
            <button
              onClick={handleRestore}
              className="w-full flex items-center justify-center space-x-2 px-4 py-2 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
              <RefreshCw size={18} />
              <span>Restore from Backup</span>
            </button>
          </div>
        </div>

        {/* Security */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md lg:col-span-2">
          <div className="p-4 border-b dark:border-gray-700">
            <h2 className="text-lg font-semibold flex items-center">
              <Shield size={20} className="mr-2" />
              Security
            </h2>
          </div>
          <div className="p-4">
            <button className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors">Change Password</button>
            <p className="text-sm text-gray-500 mt-2">Last password change: 30 days ago</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
