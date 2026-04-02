import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useSearchParams } from 'react-router-dom';
import { fetchProducts, searchProducts, filterProducts } from '../store/slices/productSlice';
import ProductCard from '../components/ProductCard';
import LoadingSpinner from '../components/LoadingSpinner';

const SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL'];
const COLORS = ['Black', 'White', 'Red', 'Blue', 'Green', 'Yellow', 'Grey'];

const ProductsPage = () => {
  const dispatch = useDispatch();
  const { products, loading, total } = useSelector((state) => state.products);
  const [searchParams, setSearchParams] = useSearchParams();

  const [query, setQuery] = useState(searchParams.get('q') || '');
  const [selectedSizes, setSelectedSizes] = useState([]);
  const [selectedColors, setSelectedColors] = useState([]);
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [category, setCategory] = useState(searchParams.get('category') || '');
  const [page, setPage] = useState(1);

  useEffect(() => {
    const params = {};
    if (query) params.q = query;
    if (category) params.category = category;
    if (selectedSizes.length) params.sizes = selectedSizes.join(',');
    if (selectedColors.length) params.colors = selectedColors.join(',');
    if (minPrice) params.min_price = minPrice;
    if (maxPrice) params.max_price = maxPrice;
    params.page = page;
    params.limit = 12;

    if (query) {
      dispatch(searchProducts({ q: query, ...params }));
    } else {
      dispatch(fetchProducts(params));
    }
  }, [dispatch, query, category, selectedSizes, selectedColors, minPrice, maxPrice, page]);

  const toggleSize = (size) => {
    setSelectedSizes((prev) => prev.includes(size) ? prev.filter((s) => s !== size) : [...prev, size]);
    setPage(1);
  };

  const toggleColor = (color) => {
    setSelectedColors((prev) => prev.includes(color) ? prev.filter((c) => c !== color) : [...prev, color]);
    setPage(1);
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setPage(1);
    setSearchParams(query ? { q: query } : {});
  };

  return (
    <div style={{ display: 'flex', maxWidth: '1200px', margin: '0 auto', padding: '40px 20px', gap: '32px' }}>
      {/* Sidebar Filters */}
      <aside style={{ width: '220px', flexShrink: 0 }}>
        <h3 style={{ marginBottom: '16px' }}>Filters</h3>

        <div style={{ marginBottom: '24px' }}>
          <h4 style={{ marginBottom: '8px' }}>Size</h4>
          {SIZES.map((s) => (
            <label key={s} style={{ display: 'block', marginBottom: '6px', cursor: 'pointer' }}>
              <input type="checkbox" checked={selectedSizes.includes(s)} onChange={() => toggleSize(s)} style={{ marginRight: '8px' }} />
              {s}
            </label>
          ))}
        </div>

        <div style={{ marginBottom: '24px' }}>
          <h4 style={{ marginBottom: '8px' }}>Color</h4>
          {COLORS.map((c) => (
            <label key={c} style={{ display: 'block', marginBottom: '6px', cursor: 'pointer' }}>
              <input type="checkbox" checked={selectedColors.includes(c)} onChange={() => toggleColor(c)} style={{ marginRight: '8px' }} />
              {c}
            </label>
          ))}
        </div>

        <div style={{ marginBottom: '24px' }}>
          <h4 style={{ marginBottom: '8px' }}>Price Range</h4>
          <input type="number" placeholder="Min $" value={minPrice} onChange={(e) => { setMinPrice(e.target.value); setPage(1); }}
            style={{ width: '100%', padding: '6px', marginBottom: '8px', border: '1px solid #ddd', borderRadius: '4px' }} />
          <input type="number" placeholder="Max $" value={maxPrice} onChange={(e) => { setMaxPrice(e.target.value); setPage(1); }}
            style={{ width: '100%', padding: '6px', border: '1px solid #ddd', borderRadius: '4px' }} />
        </div>
      </aside>

      {/* Main Content */}
      <div style={{ flex: 1 }}>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '8px', marginBottom: '32px' }}>
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search t-shirts..."
            style={{ flex: 1, padding: '10px 16px', border: '1px solid #ddd', borderRadius: '4px', fontSize: '1rem' }} />
          <button type="submit" style={{ padding: '10px 24px', background: '#1a1a2e', color: '#fff', border: 'none', borderRadius: '4px', cursor: 'pointer' }}>
            Search
          </button>
        </form>

        {loading ? (
          <LoadingSpinner />
        ) : products.length === 0 ? (
          <p style={{ textAlign: 'center', color: '#666', marginTop: '60px' }}>No products found.</p>
        ) : (
          <>
            <p style={{ marginBottom: '16px', color: '#666' }}>{total || products.length} products found</p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '24px' }}>
              {products.map((product) => (
                <ProductCard key={product._id} product={product} />
              ))}
            </div>
            {/* Pagination */}
            <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', marginTop: '40px' }}>
              <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}
                style={{ padding: '8px 16px', border: '1px solid #ddd', borderRadius: '4px', cursor: 'pointer', background: page === 1 ? '#f5f5f5' : '#fff' }}>
                Previous
              </button>
              <span style={{ padding: '8px 16px' }}>Page {page}</span>
              <button onClick={() => setPage((p) => p + 1)} disabled={products.length < 12}
                style={{ padding: '8px 16px', border: '1px solid #ddd', borderRadius: '4px', cursor: 'pointer', background: products.length < 12 ? '#f5f5f5' : '#fff' }}>
                Next
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ProductsPage;
