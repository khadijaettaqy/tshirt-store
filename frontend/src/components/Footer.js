import React from 'react';
import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-gray-300 mt-auto">
      <div className="max-w-7xl mx-auto px-4 py-10 grid grid-cols-1 md:grid-cols-4 gap-8">
        {/* Brand */}
        <div>
          <div className="flex items-center space-x-2 mb-3">
            <i className="fas fa-tshirt text-2xl text-indigo-400"></i>
            <span className="text-white text-xl font-bold">T-Shirt Store</span>
          </div>
          <p className="text-sm">Premium quality tees for every occasion. Express yourself with style.</p>
          <div className="flex space-x-4 mt-4">
            <a href="#" className="hover:text-indigo-400 transition-colors"><i className="fab fa-facebook-f"></i></a>
            <a href="#" className="hover:text-indigo-400 transition-colors"><i className="fab fa-twitter"></i></a>
            <a href="#" className="hover:text-indigo-400 transition-colors"><i className="fab fa-instagram"></i></a>
          </div>
        </div>

        {/* Shop */}
        <div>
          <h3 className="text-white font-semibold mb-3">Shop</h3>
          <ul className="space-y-2 text-sm">
            <li><Link to="/products" className="hover:text-indigo-400 transition-colors">All Products</Link></li>
            <li><Link to="/products?category=graphic" className="hover:text-indigo-400 transition-colors">Graphic Tees</Link></li>
            <li><Link to="/products?category=plain" className="hover:text-indigo-400 transition-colors">Plain Tees</Link></li>
            <li><Link to="/products?category=polo" className="hover:text-indigo-400 transition-colors">Polo Shirts</Link></li>
          </ul>
        </div>

        {/* Support */}
        <div>
          <h3 className="text-white font-semibold mb-3">Support</h3>
          <ul className="space-y-2 text-sm">
            <li><a href="#" className="hover:text-indigo-400 transition-colors">FAQ</a></li>
            <li><a href="#" className="hover:text-indigo-400 transition-colors">Contact Us</a></li>
            <li><a href="#" className="hover:text-indigo-400 transition-colors">Shipping Info</a></li>
            <li><a href="#" className="hover:text-indigo-400 transition-colors">Returns</a></li>
          </ul>
        </div>

        {/* Legal */}
        <div>
          <h3 className="text-white font-semibold mb-3">Legal</h3>
          <ul className="space-y-2 text-sm">
            <li><a href="#" className="hover:text-indigo-400 transition-colors">Privacy Policy</a></li>
            <li><a href="#" className="hover:text-indigo-400 transition-colors">Terms of Service</a></li>
            <li><a href="#" className="hover:text-indigo-400 transition-colors">Cookie Policy</a></li>
          </ul>
        </div>
      </div>

      <div className="border-t border-gray-700 py-4 text-center text-sm">
        <p>&copy; {new Date().getFullYear()} T-Shirt Store. All rights reserved.</p>
      </div>
    </footer>
  );
}
