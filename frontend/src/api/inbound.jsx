import api from "./axios";

export const getInbounds = async () => {
  const res = await api.get("/inbounds");
  return res.data;
};

export const createInbound = async (data) => {
  const res = await api.post("/inbounds", data);
  return res.data;
};