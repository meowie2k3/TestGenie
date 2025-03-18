import Api from './Api';

export const fetchDiagramData = async (git_url) => {
    const response = await Api.post('/getDiagram', { git_url });
    return response.data;
};