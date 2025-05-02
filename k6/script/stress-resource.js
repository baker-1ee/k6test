import http from 'k6/http';
import { check } from 'k6';
import { Trend } from 'k6/metrics';

let ttfb = new Trend('a_ttfb', true);
let download = new Trend('b_download_time', true);
let total = new Trend('c_total_duration', true);

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

const urls = [
    'https://your-company.com/assets/js/vconsole.min.js',
    'https://your-cdn.net/your-font.woff',
];

export default function () {
    const requests = urls.map((url) => ['GET', url, null, { tags: { resource: url } }]);
    const responses = http.batch(requests);

    for (let i = 0; i < responses.length; i++) {
        const res = responses[i];
        const url = urls[i];

        const isValid = res.status === 200;

        check(res, {
            [`valid static ${url}`]: () => isValid,
        });

        if (isValid) {
            ttfb.add(res.timings.waiting, { resource: url });
            download.add(res.timings.receiving, { resource: url });
            total.add(res.timings.duration, { resource: url });
        }
    }
}
