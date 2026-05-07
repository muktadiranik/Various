import { useMemo } from "react";
import axiosInstance from "../api/axios";

export default function useApi() {
  return useMemo(() => axiosInstance, []);
}
