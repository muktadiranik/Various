import { configureStore } from "@reduxjs/toolkit";
import authSlice from "./authSlice.js";
import productSlice from "./productSlice.js";

export const store = configureStore({
  reducer: {
    auth: authSlice,
    products: productSlice,
  },
});
