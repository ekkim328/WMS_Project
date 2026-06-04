import api from "./axios";

export const getInventories = async () => {
  const res = await api.get("/inventory");
  return res.data;
};