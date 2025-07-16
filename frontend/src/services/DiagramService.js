import Api from './api';

export const fetchDiagramData = async (git_url) => {
    const response = await Api.post('/getDiagram', { git_url });
    return response.data;
};

export const fetchBlockDetails = async (git_url, block_id) => {
    const response = await Api.post('/getBlockDetail', { git_url, block_id });
    return response.data;
}

export const savePrediction = async (git_url, block_id, prediction) => {
    const response = await Api.post('/updateBlockPrediction', { git_url, block_id, prediction });
    return response.data;
}

export const generateTest = async (git_url, block_id) => {
    const response = await Api.post('/generateTest', { git_url, block_id });
    return response.data;
}