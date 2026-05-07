import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { productsAPI } from "../services/api";

export const fetchProducts = createAsyncThunk("products/fetchProducts", async () => {
  const response = await productsAPI.products();
  return response;
});

export const fetchCategories = createAsyncThunk("products/fetchCategories", async () => {
  const response = await productsAPI.categories();
  return response;
});

export const createProduct = createAsyncThunk("products/createProduct", async (data, { dispatch }) => {
  const response = await productsAPI.createProduct(data);
  dispatch(fetchProducts()); // refetch list
  return response;
});

export const updateProduct = createAsyncThunk("products/updateProduct", async ({ id, data }, { dispatch }) => {
  const response = await productsAPI.updateProduct(id, data);
  dispatch(fetchProducts());
  return response;
});

const productSlice = createSlice({
  name: "products",
  initialState: {
    products: [],
    categories: [],
    loading: false,
    formLoading: false,
    error: null,
  },
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    resetFormLoading: (state) => {
      state.formLoading = false;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchProducts.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchProducts.fulfilled, (state, action) => {
        state.loading = false;
        state.products = action.payload;
      })
      .addCase(fetchProducts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      })
      .addCase(fetchCategories.fulfilled, (state, action) => {
        state.categories = action.payload;
      })
      .addCase(createProduct.pending, (state) => {
        state.formLoading = true;
      })
      .addCase(createProduct.fulfilled, (state) => {
        state.formLoading = false;
      })
      .addCase(createProduct.rejected, (state, action) => {
        state.formLoading = false;
        state.error = action.error.message;
      })
      .addCase(updateProduct.pending, (state) => {
        state.formLoading = true;
      })
      .addCase(updateProduct.fulfilled, (state) => {
        state.formLoading = false;
      })
      .addCase(updateProduct.rejected, (state, action) => {
        state.formLoading = false;
        state.error = action.error.message;
      });
  },
});

export const { clearError, resetFormLoading } = productSlice.actions;
export default productSlice.reducer;
