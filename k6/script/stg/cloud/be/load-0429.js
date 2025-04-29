import http from 'k6/http';
import {check, sleep} from 'k6';

function toQueryString(params) {
    if (!params || typeof params !== 'object') return '';
    return Object.entries(params)
        .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
        .join('&');
}

export let options = {
    vus: __ENV.VUS ? parseInt(__ENV.VUS) : 10,
    duration: __ENV.DURATION || '1m',
};

const BASE_URL = 'https://stg-app.hyundaicapital.com';

export default function () {

    const apiList = [
        {name: '상품별 금리 조회', method: 'GET', path: '/web/lon/hm/LONHM010301.do'},
    ];

    const commonHeaders = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    // 나머지 API 순차 호출
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
