import api from "./axios";

export const getProducts = async () => {
  const res = await api.get("/products");
  return res.data;
};

export const getLocationOptions = async (productId) => {
  const res = await api.get("/inventories/location-options", {
    params: { product_id: productId },
  });
  return res.data;
};
