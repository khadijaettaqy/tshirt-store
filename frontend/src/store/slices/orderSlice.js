import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

export const createOrder = createAsyncThunk('orders/create', async (data, thunkAPI) => {
  try {
    const res = await api.post('/orders/', data);
    return res.data;
  } catch (err) {
    return thunkAPI.rejectWithValue(err.response?.data?.error || 'Failed to create order');
  }
});

export const fetchOrders = createAsyncThunk('orders/fetchAll', async (params = {}, thunkAPI) => {
  try {
    const res = await api.get('/orders/', { params });
    return res.data;
  } catch (err) {
    return thunkAPI.rejectWithValue(err.response?.data?.error || 'Failed to fetch orders');
  }
});

export const fetchOrder = createAsyncThunk('orders/fetchOne', async (id, thunkAPI) => {
  try {
    const res = await api.get(`/orders/${id}`);
    return res.data.order;
  } catch (err) {
    return thunkAPI.rejectWithValue(err.response?.data?.error || 'Failed to fetch order');
  }
});

export const confirmPayment = createAsyncThunk('orders/confirmPayment', async ({ orderId, paymentIntentId }, thunkAPI) => {
  try {
    const res = await api.post(`/orders/${orderId}/confirm-payment`, { payment_intent_id: paymentIntentId });
    return res.data.order;
  } catch (err) {
    return thunkAPI.rejectWithValue(err.response?.data?.error || 'Failed to confirm payment');
  }
});

const orderSlice = createSlice({
  name: 'orders',
  initialState: {
    orders: [],
    currentOrder: null,
    clientSecret: null,
    loading: false,
    error: null,
    pagination: { page: 1, pages: 1, total: 0 },
  },
  reducers: {
    clearCurrentOrder: (state) => {
      state.currentOrder = null;
      state.clientSecret = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(createOrder.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(createOrder.fulfilled, (state, action) => {
        state.loading = false;
        state.currentOrder = action.payload.order;
        state.clientSecret = action.payload.client_secret;
      })
      .addCase(createOrder.rejected, (state, action) => { state.loading = false; state.error = action.payload; })
      .addCase(fetchOrders.pending, (state) => { state.loading = true; })
      .addCase(fetchOrders.fulfilled, (state, action) => {
        state.loading = false;
        state.orders = action.payload.orders;
        state.pagination = { page: action.payload.page, pages: action.payload.pages, total: action.payload.total };
      })
      .addCase(fetchOrders.rejected, (state, action) => { state.loading = false; state.error = action.payload; })
      .addCase(fetchOrder.fulfilled, (state, action) => { state.loading = false; state.currentOrder = action.payload; })
      .addCase(confirmPayment.fulfilled, (state, action) => {
        state.currentOrder = action.payload;
        const idx = state.orders.findIndex(o => o.id === action.payload.id);
        if (idx !== -1) state.orders[idx] = action.payload;
      });
  },
});

export const { clearCurrentOrder } = orderSlice.actions;
export default orderSlice.reducer;
