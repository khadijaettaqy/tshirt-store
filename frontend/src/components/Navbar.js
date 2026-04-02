import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { logoutUser } from '../store/slices/authSlice';

export default function Navbar() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useSelector((state) => state.auth);
  const { item_count } = useSelector((state) => state.cart);
  const [menuOpen, setMenuOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const handleLogout = async () => {
    await dispatch(logoutUser());
    navigate('/login');
    setUserMenuOpen(false);
  };

  return (
    <nav className="bg-gray-900 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <i className="fas fa-tshirt text-2xl text-indigo-400"></i>
            <span className="text-xl font-bold">T-Shirt Store</span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center space-x-6">
            <Link to="/" className="hover:text-indigo-400 transition-colors">Home</Link>
            <Link to="/products" className="hover:text-indigo-400 transition-colors">Products</Link>
            {isAuthenticated && (
              <Link to="/wishlist" className="hover:text-indigo-400 transition-colors">
                <i className="fas fa-heart mr-1"></i>Wishlist
              </Link>
            )}
          </div>

          {/* Right section */}
          <div className="hidden md:flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                {/* Cart */}
                <Link to="/cart" className="relative hover:text-indigo-400 transition-colors">
                  <i className="fas fa-shopping-cart text-xl"></i>
                  {item_count > 0 && (
                    <span className="absolute -top-2 -right-2 bg-indigo-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                      {item_count > 99 ? '99+' : item_count}
                    </span>
                  )}
                </Link>

                {/* User Menu */}
                <div className="relative">
                  <button
                    onClick={() => setUserMenuOpen(!userMenuOpen)}
                    className="flex items-center space-x-2 hover:text-indigo-400 transition-colors"
                  >
                    <i className="fas fa-user-circle text-xl"></i>
                    <span>{user?.full_name?.split(' ')[0] || 'Account'}</span>
                    <i className="fas fa-chevron-down text-xs"></i>
                  </button>
                  {userMenuOpen && (
                    <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-50">
                      <div className="py-1">
                        <Link to="/profile" onClick={() => setUserMenuOpen(false)}
                          className="block px-4 py-2 text-gray-700 hover:bg-gray-100">
                          <i className="fas fa-user mr-2"></i>Profile
                        </Link>
                        <Link to="/orders" onClick={() => setUserMenuOpen(false)}
                          className="block px-4 py-2 text-gray-700 hover:bg-gray-100">
                          <i className="fas fa-box mr-2"></i>Orders
                        </Link>
                        {user?.role === 'admin' && (
                          <Link to="/admin" onClick={() => setUserMenuOpen(false)}
                            className="block px-4 py-2 text-gray-700 hover:bg-gray-100">
                            <i className="fas fa-cog mr-2"></i>Admin Panel
                          </Link>
                        )}
                        <hr className="my-1" />
                        <button onClick={handleLogout}
                          className="block w-full text-left px-4 py-2 text-red-600 hover:bg-gray-100">
                          <i className="fas fa-sign-out-alt mr-2"></i>Logout
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <>
                <Link to="/login" className="hover:text-indigo-400 transition-colors">Login</Link>
                <Link to="/register"
                  className="bg-indigo-600 px-4 py-2 rounded-md hover:bg-indigo-700 transition-colors">
                  Register
                </Link>
              </>
            )}
          </div>

          {/* Mobile menu button */}
          <button className="md:hidden" onClick={() => setMenuOpen(!menuOpen)}>
            <i className={`fas ${menuOpen ? 'fa-times' : 'fa-bars'} text-xl`}></i>
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {menuOpen && (
        <div className="md:hidden bg-gray-800 px-4 pt-2 pb-4 space-y-2">
          <Link to="/" onClick={() => setMenuOpen(false)} className="block py-2 hover:text-indigo-400">Home</Link>
          <Link to="/products" onClick={() => setMenuOpen(false)} className="block py-2 hover:text-indigo-400">Products</Link>
          {isAuthenticated ? (
            <>
              <Link to="/cart" onClick={() => setMenuOpen(false)} className="block py-2 hover:text-indigo-400">
                Cart {item_count > 0 && <span className="ml-1 bg-indigo-500 text-xs px-2 py-0.5 rounded-full">{item_count}</span>}
              </Link>
              <Link to="/wishlist" onClick={() => setMenuOpen(false)} className="block py-2 hover:text-indigo-400">Wishlist</Link>
              <Link to="/profile" onClick={() => setMenuOpen(false)} className="block py-2 hover:text-indigo-400">Profile</Link>
              <Link to="/orders" onClick={() => setMenuOpen(false)} className="block py-2 hover:text-indigo-400">Orders</Link>
              {user?.role === 'admin' && (
                <Link to="/admin" onClick={() => setMenuOpen(false)} className="block py-2 hover:text-indigo-400">Admin Panel</Link>
              )}
              <button onClick={handleLogout} className="block py-2 text-red-400 w-full text-left">Logout</button>
            </>
          ) : (
            <>
              <Link to="/login" onClick={() => setMenuOpen(false)} className="block py-2 hover:text-indigo-400">Login</Link>
              <Link to="/register" onClick={() => setMenuOpen(false)} className="block py-2 hover:text-indigo-400">Register</Link>
            </>
          )}
        </div>
      )}
    </nav>
  );
}
