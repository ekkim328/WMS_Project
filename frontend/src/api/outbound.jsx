import api from "./axios";

export const getOutbounds = async () => {
  const res = await api.get("/outbounds");
  return res.data;
};

export const getOutboundForecast = async () => {
  const res = await api.get("/outbounds/forecast");
  return res.data;
};

export const createOutbound = async (data) => {
  const res = await api.post("/outbounds", data);
  return res.data;
};
