import http from 'k6/http';
import {check} from 'k6';

function toQueryString(params) {
    if (!params || typeof params !== 'object') return '';
    return Object.entries(params)
        .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
        .join('&');
}

export let options = {
    stages: [
        { duration: '1m', target: 50 },
        { duration: '1m', target: 100 },
        { duration: '1m', target: 500 },
        { duration: '2m', target: 1000 },
        { duration: '3m', target: 1000 },
        { duration: '2m', target: 0 },
    ],
};

const BASE_URL = 'https://your-company.com';
const ID = 'member-id'

export default function () {

    const initApi = {name: '로그인', method: 'POST', path: '/auth/login', params: {id: 'your-id', password: 'your-password'}};
    const apiList = [
        {name: '회원 정보 조회', method: 'GET', path: `/v1/members/${ID}`},
        {name: '알람 목록 조회', method: 'GET', path: '/v1/alarms'},
    ];

    const initUrl = `${BASE_URL}${initApi.path}`;
    const initBody = JSON.stringify(initApi.params);
    const initRes = http.post(initUrl, initBody, {headers: {'Content-Type': 'application/json'}});
    const cookieHeader = initRes.headers['Set-Cookie'];
    const jsessionId = cookieHeader?.match(/JSESSIONID=([^;]+)/)?.[1];

    check(jsessionId, {
        'JSESSIONID was extracted ': (v) => !!v
    });

    const commonHeaders = {
        headers: {
            'Content-Type': 'application/json',
            'Cookie': `JSESSIONID=${jsessionId}`,
        },
    };

    for (let i = 0; i < apiList.length; i++) {
        const {name, method, path, params} = apiList[i];
        const url = `${BASE_URL}${path}`;

        let res;
        if (method === 'GET') {
            const query = toQueryString(params);
            const fullUrl = query ? `${url}?${query}` : url;
            res = http.get(fullUrl, commonHeaders);
        } else if (method === 'POST') {
            const body = params ? JSON.stringify(params) : '';
            res = http.post(url, body, commonHeaders);
        }

        check(res, {
            [`${name} ${method} ${path} is 200`]: (r) => r.status === 200,
        });
    }
}
