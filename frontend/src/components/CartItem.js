import React from 'react';
import { useDispatch } from 'react-redux';
import { removeFromCart, updateQuantity } from '../store/slices/cartSlice';

export default function CartItem({ item }) {
  const dispatch = useDispatch();
  const imageUrl = item.image || `https://via.placeholder.com/100x100?text=${encodeURIComponent(item.name || 'Item')}`;

  return (
    <div className="flex items-center gap-4 py-4 border-b">
      <img src={imageUrl} alt={item.name} className="w-20 h-20 object-cover rounded-lg" onError={(e)=>{e.target.src='https://via.placeholder.com/100x100?text=Item'}} />
      <div className="flex-grow">
        <h3 className="font-semibold text-gray-800">{item.name}</h3>
        <p className="text-sm text-gray-500">Size: {item.size} | Color: {item.color}</p>
        <p className="text-indigo-600 font-bold">${(item.price * item.quantity).toFixed(2)}</p>
      </div>
      <div className="flex items-center gap-2">
        <button onClick={() => dispatch(updateQuantity({ product_id: item.product_id, size: item.size, color: item.color, quantity: item.quantity - 1 }))}
          disabled={item.quantity <= 1}
          className="w-8 h-8 rounded-full border border-gray-300 hover:bg-gray-100 disabled:opacity-40">-</button>
        <span className="w-8 text-center font-semibold">{item.quantity}</span>
        <button onClick={() => dispatch(updateQuantity({ product_id: item.product_id, size: item.size, color: item.color, quantity: item.quantity + 1 }))}
          className="w-8 h-8 rounded-full border border-gray-300 hover:bg-gray-100">+</button>
      </div>
      <button onClick={() => dispatch(removeFromCart({ product_id: item.product_id, size: item.size, color: item.color }))}
        className="text-red-500 hover:text-red-700 ml-2">
        <i className="fas fa-trash"></i>
      </button>
    </div>
  );
}
