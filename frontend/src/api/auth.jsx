import api from "./axios";

export const signup = async ({ username, name, password }) => {
  const res = await api.post("/users", {
    username,
    name,
    password,
  });

  return res.data;
};

export const login = async (username, password) => {
  const formData = new URLSearchParams();

  formData.append("username", username);
  formData.append("password", password);

  const res = await api.post("/users/token", formData, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });

  localStorage.setItem("access_token", res.data.access_token);

  return res.data;
};
