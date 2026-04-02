import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { fetchProducts } from '../store/slices/productSlice';
import ProductCard from '../components/ProductCard';
import LoadingSpinner from '../components/LoadingSpinner';

const HomePage = () => {
  const dispatch = useDispatch();
  const { products, loading } = useSelector((state) => state.products);

  useEffect(() => {
    dispatch(fetchProducts({ limit: 8 }));
  }, [dispatch]);

  const featured = products.slice(0, 8);

  return (
    <div>
      {/* Hero */}
      <section style={{ background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)', color: '#fff', padding: '80px 20px', textAlign: 'center' }}>
        <h1 style={{ fontSize: '3rem', marginBottom: '16px' }}>Premium T-Shirts</h1>
        <p style={{ fontSize: '1.2rem', marginBottom: '32px', opacity: 0.8 }}>Quality fabrics, bold designs. Shop the latest collection.</p>
        <Link to="/products" style={{ background: '#e94560', color: '#fff', padding: '14px 36px', borderRadius: '4px', textDecoration: 'none', fontSize: '1.1rem', fontWeight: 600 }}>
          Shop Now
        </Link>
      </section>

      {/* Featured Products */}
      <section style={{ padding: '60px 40px', maxWidth: '1200px', margin: '0 auto' }}>
        <h2 style={{ textAlign: 'center', marginBottom: '40px', fontSize: '2rem' }}>Featured Products</h2>
        {loading ? (
          <LoadingSpinner />
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '24px' }}>
            {featured.map((product) => (
              <ProductCard key={product._id} product={product} />
            ))}
          </div>
        )}
        <div style={{ textAlign: 'center', marginTop: '40px' }}>
          <Link to="/products" style={{ background: '#1a1a2e', color: '#fff', padding: '12px 32px', borderRadius: '4px', textDecoration: 'none' }}>
            View All Products
          </Link>
        </div>
      </section>

      {/* Categories */}
      <section style={{ background: '#f5f5f5', padding: '60px 40px' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <h2 style={{ textAlign: 'center', marginBottom: '40px', fontSize: '2rem' }}>Shop by Category</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '20px' }}>
            {['Graphic Tees', 'Plain', 'V-Neck', 'Long Sleeve', 'Polo', 'Sports'].map((cat) => (
              <Link key={cat} to={`/products?category=${encodeURIComponent(cat)}`}
                style={{ display: 'block', background: '#fff', padding: '32px', textAlign: 'center', borderRadius: '8px', textDecoration: 'none', color: '#1a1a2e', fontWeight: 600, boxShadow: '0 2px 8px rgba(0,0,0,0.08)', transition: 'transform 0.2s' }}>
                {cat}
              </Link>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
