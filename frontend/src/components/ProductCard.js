import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { addToCart } from '../store/slices/cartSlice';
import api from '../services/api';

export default function ProductCard({ product }) {
  const dispatch = useDispatch();
  const { isAuthenticated } = useSelector((state) => state.auth);
  const [selectedSize, setSelectedSize] = useState('');
  const [selectedColor, setSelectedColor] = useState(product.colors?.[0] || '');
  const [addingToCart, setAddingToCart] = useState(false);
  const [wishlistLoading, setWishlistLoading] = useState(false);
  const [inWishlist, setInWishlist] = useState(false);
  const [message, setMessage] = useState('');

  const handleAddToCart = async (e) => {
    e.preventDefault();
    if (!selectedSize) {
      setMessage('Please select a size');
      setTimeout(() => setMessage(''), 2000);
      return;
    }
    setAddingToCart(true);
    await dispatch(addToCart({
      product_id: product.id,
      size: selectedSize,
      color: selectedColor,
      quantity: 1,
    }));
    setAddingToCart(false);
    setMessage('Added to cart!');
    setTimeout(() => setMessage(''), 2000);
  };

  const handleWishlistToggle = async (e) => {
    e.preventDefault();
    if (!isAuthenticated) return;
    setWishlistLoading(true);
    try {
      if (inWishlist) {
        await api.delete(`/users/wishlist/${product.id}`);
        setInWishlist(false);
      } else {
        await api.post(`/users/wishlist/${product.id}`);
        setInWishlist(true);
      }
    } catch (err) {
      // ignore
    }
    setWishlistLoading(false);
  };

  const renderStars = (rating) => {
    return Array.from({ length: 5 }, (_, i) => (
      <i key={i} className={`fas fa-star text-xs ${i < Math.round(rating) ? 'text-yellow-400' : 'text-gray-300'}`}></i>
    ));
  };

  const imageUrl = product.images?.[0] || `https://via.placeholder.com/300x300?text=${encodeURIComponent(product.name)}`;

  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300 flex flex-col">
      <Link to={`/products/${product.id}`} className="relative">
        <img
          src={imageUrl}
          alt={product.name}
          className="w-full h-56 object-cover"
          onError={(e) => { e.target.src = `https://via.placeholder.com/300x300?text=${encodeURIComponent(product.name)}`; }}
        />
        {isAuthenticated && (
          <button
            onClick={handleWishlistToggle}
            disabled={wishlistLoading}
            className="absolute top-2 right-2 bg-white bg-opacity-80 p-2 rounded-full shadow hover:bg-opacity-100 transition-all"
          >
            <i className={`fas fa-heart ${inWishlist ? 'text-red-500' : 'text-gray-400'}`}></i>
          </button>
        )}
      </Link>

      <div className="p-4 flex flex-col flex-grow">
        <Link to={`/products/${product.id}`}>
          <h3 className="font-semibold text-gray-800 hover:text-indigo-600 transition-colors line-clamp-2">{product.name}</h3>
        </Link>

        <div className="flex items-center mt-1">
          <div className="flex">{renderStars(product.avg_rating || 0)}</div>
          <span className="text-xs text-gray-500 ml-1">({product.num_reviews || 0})</span>
        </div>

        <p className="text-xl font-bold text-indigo-600 mt-2">${product.price?.toFixed(2)}</p>

        {/* Size selector */}
        {product.sizes && product.sizes.length > 0 && (
          <div className="mt-3">
            <p className="text-xs text-gray-500 mb-1">Size:</p>
            <div className="flex flex-wrap gap-1">
              {product.sizes.map((s) => (
                <button
                  key={s.size}
                  onClick={() => setSelectedSize(s.size)}
                  disabled={s.stock === 0}
                  className={`px-2 py-1 text-xs border rounded ${
                    selectedSize === s.size
                      ? 'bg-indigo-600 text-white border-indigo-600'
                      : s.stock === 0
                      ? 'bg-gray-100 text-gray-400 line-through cursor-not-allowed'
                      : 'border-gray-300 hover:border-indigo-400'
                  }`}
                >
                  {s.size}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Color selector */}
        {product.colors && product.colors.length > 1 && (
          <div className="mt-2">
            <p className="text-xs text-gray-500 mb-1">Color:</p>
            <div className="flex flex-wrap gap-1">
              {product.colors.map((c) => (
                <button
                  key={c}
                  onClick={() => setSelectedColor(c)}
                  className={`px-2 py-1 text-xs border rounded ${
                    selectedColor === c ? 'bg-indigo-600 text-white border-indigo-600' : 'border-gray-300 hover:border-indigo-400'
                  }`}
                >
                  {c}
                </button>
              ))}
            </div>
          </div>
        )}

        {message && (
          <p className={`text-xs mt-2 ${message.includes('Added') ? 'text-green-600' : 'text-red-500'}`}>{message}</p>
        )}

        <button
          onClick={handleAddToCart}
          disabled={addingToCart}
          className="mt-auto mt-3 w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50 text-sm font-medium"
        >
          {addingToCart ? <><i className="fas fa-spinner fa-spin mr-2"></i>Adding...</> : <><i className="fas fa-cart-plus mr-2"></i>Add to Cart</>}
        </button>
      </div>
    </div>
  );
}
