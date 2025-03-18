import axios from 'axios';

export default function Api () {
    return axios.create({
        baseURL: 'http://127.0.0.1:5000'
    })
}
