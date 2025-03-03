import axios from "axios";

export const fetchGraphData = async (repo) => {
  const response = await axios.get(`https://your-api.com/analyze?repo=${repo}`);
  return response.data;
};
