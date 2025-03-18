import Api from './Api';

export async function fetchDiagramData (git_url) {
    return Api().post('/getDiagram', {
        git_url: git_url
    }).then((response) => {
        return response;
    }).catch((error) => {
        console.error(error);
    });
}