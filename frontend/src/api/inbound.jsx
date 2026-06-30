import api from "./axios";

export const getInbounds = async () => {
  const res = await api.get("/inbounds");
  return res.data;
};

export const getInboundForecast = async ({ product_id }) => {
  const res = await api.get("/inbounds/forecast", {
    params: { product_id },
  });
  return res.data;
};

export const getInboundLocationRecommendation = async ({ product_id, inbound_qty }) => {
  const res = await api.get("/inbounds/location-recommendation", {
    params: { product_id, inbound_qty },
  });
  return res.data;
};

export const createInbound = async (data) => {
  const res = await api.post("/inbounds", data);
  return res.data;
};
