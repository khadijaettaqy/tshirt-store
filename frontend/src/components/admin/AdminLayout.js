import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';

export default function AdminLayout() {
  const links = [
    { to: '/admin', label: 'Dashboard', icon: 'fa-tachometer-alt', end: true },
    { to: '/admin/products', label: 'Products', icon: 'fa-tshirt' },
    { to: '/admin/orders', label: 'Orders', icon: 'fa-box' },
    { to: '/admin/users', label: 'Users', icon: 'fa-users' },
    { to: '/admin/navigation', label: 'Navigation', icon: 'fa-chart-line' },
  ];
  return (
    <div className="flex min-h-screen bg-gray-100">
      <aside className="w-64 bg-gray-900 text-white">
        <div className="p-4 border-b border-gray-700">
          <h2 className="text-xl font-bold text-indigo-400">Admin Panel</h2>
        </div>
        <nav className="p-4 space-y-1">
          {links.map(l => (
            <NavLink key={l.to} to={l.to} end={l.end}
              className={({ isActive }) => `flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${isActive ? 'bg-indigo-600' : 'hover:bg-gray-700'}`}>
              <i className={`fas ${l.icon} w-5`}></i>{l.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="flex-1 p-8 overflow-auto"><Outlet /></main>
    </div>
  );
}
