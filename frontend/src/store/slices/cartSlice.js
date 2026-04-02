import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

export const fetchCart = createAsyncThunk('cart/fetch', async (_, thunkAPI) => {
  try {
    const res = await api.get('/cart/');
    return res.data.cart;
  } catch (err) {
    return thunkAPI.rejectWithValue(err.response?.data?.error || 'Failed to fetch cart');
  }
});

export const addToCart = createAsyncThunk('cart/add', async (item, thunkAPI) => {
  try {
    const res = await api.post('/cart/add', item);
    return res.data.cart;
  } catch (err) {
    return thunkAPI.rejectWithValue(err.response?.data?.error || 'Failed to add to cart');
  }
});

export const removeFromCart = createAsyncThunk('cart/remove', async (item, thunkAPI) => {
  try {
    const res = await api.delete('/cart/remove', { data: item });
    return res.data.cart;
  } catch (err) {
    return thunkAPI.rejectWithValue(err.response?.data?.error || 'Failed to remove from cart');
  }
});

export const updateQuantity = createAsyncThunk('cart/updateQuantity', async (item, thunkAPI) => {
  try {
    const res = await api.put('/cart/update', item);
    return res.data.cart;
  } catch (err) {
    return thunkAPI.rejectWithValue(err.response?.data?.error || 'Failed to update cart');
  }
});

export const clearCart = createAsyncThunk('cart/clear', async (_, thunkAPI) => {
  try {
    await api.delete('/cart/clear');
    return { items: [], item_count: 0 };
  } catch (err) {
    return thunkAPI.rejectWithValue(err.response?.data?.error || 'Failed to clear cart');
  }
});

const cartSlice = createSlice({
  name: 'cart',
  initialState: {
    items: [],
    item_count: 0,
    loading: false,
    error: null,
  },
  reducers: {
    clearCartState: (state) => {
      state.items = [];
      state.item_count = 0;
    },
  },
  extraReducers: (builder) => {
    const setCart = (state, action) => {
      state.loading = false;
      state.items = action.payload.items || [];
      state.item_count = action.payload.item_count || 0;
    };
    builder
      .addCase(fetchCart.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(fetchCart.fulfilled, setCart)
      .addCase(fetchCart.rejected, (state, action) => { state.loading = false; state.error = action.payload; })
      .addCase(addToCart.pending, (state) => { state.loading = true; })
      .addCase(addToCart.fulfilled, setCart)
      .addCase(addToCart.rejected, (state, action) => { state.loading = false; state.error = action.payload; })
      .addCase(removeFromCart.fulfilled, setCart)
      .addCase(updateQuantity.fulfilled, setCart)
      .addCase(clearCart.fulfilled, setCart);
  },
});

export const { clearCartState } = cartSlice.actions;
export default cartSlice.reducer;
