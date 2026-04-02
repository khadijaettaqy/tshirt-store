import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '../../services/api';

export const trackNavigation = createAsyncThunk('navigation/track', async (data, thunkAPI) => {
  try {
    const res = await api.post('/navigation/track', data);
    return res.data;
  } catch (err) {
    return thunkAPI.rejectWithValue(err.response?.data?.error || 'Tracking failed');
  }
});

export const fetchHistory = createAsyncThunk('navigation/fetchHistory', async (_, thunkAPI) => {
  try {
    const res = await api.get('/navigation/history');
    return res.data.history;
  } catch (err) {
    return thunkAPI.rejectWithValue(err.response?.data?.error || 'Failed to fetch history');
  }
});

export const fetchAnalytics = createAsyncThunk('navigation/fetchAnalytics', async (params = {}, thunkAPI) => {
  try {
    const res = await api.get('/navigation/admin/analytics', { params });
    return res.data;
  } catch (err) {
    return thunkAPI.rejectWithValue(err.response?.data?.error || 'Failed to fetch analytics');
  }
});

const navigationSlice = createSlice({
  name: 'navigation',
  initialState: {
    history: [],
    currentSession: { id: null, startTime: null },
    analytics: {},
    loading: false,
    error: null,
  },
  reducers: {
    setSessionId: (state, action) => {
      state.currentSession = { id: action.payload, startTime: Date.now() };
    },
    addToHistory: (state, action) => {
      state.history.unshift(action.payload);
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchHistory.fulfilled, (state, action) => {
        state.history = action.payload;
      })
      .addCase(fetchAnalytics.pending, (state) => { state.loading = true; })
      .addCase(fetchAnalytics.fulfilled, (state, action) => {
        state.loading = false;
        state.analytics = action.payload;
      })
      .addCase(fetchAnalytics.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { setSessionId, addToHistory } = navigationSlice.actions;
export default navigationSlice.reducer;
