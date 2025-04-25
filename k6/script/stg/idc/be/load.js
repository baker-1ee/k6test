import http from 'k6/http';
import {check, sleep} from 'k6';

function toQueryString(params) {
    if (!params || typeof params !== 'object') return '';
    return Object.entries(params)
        .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
        .join('&');
}

function getTodayString() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');

    return `${year}${month}${day}`;
}

export let options = {
    vus: __ENV.VUS ? parseInt(__ENV.VUS) : 30,
    duration: __ENV.DURATION || '10m',
};

const BASE_URL = 'https://stg-app2v.hyundaicapital.com';
const APP_UUID = 'anftest01';
const TODAY = getTodayString();
const CUST_NO_LIST = [
    '1683988666', '1982192509', '1191691321', '1582174705', '1787267327', '1491149844', '1919722069'
];

export default function () {

    const CUST_NO = CUST_NO_LIST[Math.floor(Math.random() * CUST_NO_LIST.length)];

    const initApi = {
        name: '00.초기화',
        method: 'POST',
        path: '/api/ini/in/INIIN010101.do',
        params: {
            appnVrsn: '4.0.2',
            dvceNm: 'HC1',
            dvceTokn: 'HC2',
            dvceUuid: APP_UUID,
            modlNm: 'LGM-G600L',
            osType: 'A',
            osVrsn: '10.0',
            scurKeypadUuid: ''
        }
    };
    const apiList = [
        {name: '00.테스트 로그인', method: 'POST', path: '/api/lgn/ts/LGNTS010101.do', params: {apcaUserYn: 'N', pwd_key: '112233', pwd_ltn: '112233', xbh1Cltn: CUST_NO}},
        {name: '01.자담 캠페인 조회', method: 'GET', path: '/web/mah/li/MAHLI010201.do'},
        {name: '02.APP 대출 배너 조회 조건', method: 'GET', path: '/web/lon/il/LONIL020101.do'},
        {name: '03.지문인증 등록여부 확인', method: 'GET', path: '/web/set/av/SETAV010201.do'},
        {name: '04.마이데이터 약관 동의여부 및 연동여부 조회', method: 'GET', path: '/web/gcm/gc/GCMGC040101.do'},
        {name: '05.근저당설정해지 목록조회', method: 'POST', path: '/web/mya/ca/MYACA010101.do', params: {isChkYn: 'N'}},
        {name: '06.알림함 신규 컨텐츠 개수 조회', method: 'GET', path: '/v1/notification/contents/count/new'},
        {name: '07.푸시 메세지 리스트 조회', method: 'POST', path: '/web/mah/nb/MAHNB010101.do', params: {}},
        {name: '08.추천 차량 목록 조회', method: 'GET', path: '/v1/recommendation/cars.do', params: {userId: CUST_NO, 'slot-id': '000001'}},
        {name: '09.금융 영업일 조회', method: 'GET', path: '/v1/date/finance/business-days-after', params: {days: '5'}},
        {name: '10.쇼룸 대표 차량 목록 조회', method: 'GET', path: '/v1/showroom/car/representatives', params: {category: 'ALL'}},
        {name: '11.진행중인 이벤트 목록 조회', method: 'GET', path: '/v1/events', params: {category: 'DIRECT_CAR'}},
        {name: '12.보관함 컨텐츠 조회', method: 'GET', path: '/v1/locker/contents', params: {lockerType: 'ALL', isMember: true}},
        {name: '13.상품이용 조회', method: 'POST', path: '/web/mah/pu/MAHPU010102.do', params: {cardInfoIqryYn: '', clscStupYn: '', endYn: 'N', requestCount: '', sortYn: 'N', stlmDdChngYn: '', stmtRcivMathYn: ''}},
        {name: '14.내자산 차량 정보 조회', method: 'GET', path: '/v1/me/assets/cars'},
        {name: '15.내자산 중 기타 정보', method: 'GET', path: '/v1/me/assets/etc'},
        {name: '16.약관동의여부 조회', method: 'GET', path: '/web/myd/ag/MYDAG010106.do'},
        {name: '17.보관함 컨텐츠 조회', method: 'GET', path: '/v1/locker/contents', params: {lockerType: 'ALL', isMember: true}},
        {name: '18.홈카드 조회', method: 'POST', path: '/v1/users/me/home-cards', params: {login: true, custNo: CUST_NO, appUuid: APP_UUID}},
        {name: '19.푸시 메세지 건수 조회', method: 'POST', path: '/web/mah/nb/MAHNB010201.do', params: {}},
        {name: '20.내 차량 조회', method: 'GET', path: '/v1/users/me/cars/simple'},
        {name: '21.나의 배너 차량 조회', method: 'GET', path: '/v1/users/me/banners/car'},
        {name: '22.MYDATA용 CI값 존재 여부 조회', method: 'GET', path: '/web/myd/ag/MYDAG020103.do'},
        {name: '23.상품이용 조회', method: 'POST', path: '/web/mah/pu/MAHPU010102.do', params: {cardInfoIqryYn: '', clscStupYn: '', endYn: 'N', requestCount: '', sortYn: 'N', stlmDdChngYn: '', stmtRcivMathYn: ''}},
        {name: '24.대출정보 조회', method: 'GET', path: '/web/mah/li/MAHLI010101.do'},
        {name: '25.클라이언트 로그 저장', method: 'POST', path: '/v1/log/client/user/behavior', params: {events: []}},
        {name: '26.신용 점수 조회', method: 'GET', path: '/v1/users/me/credit-score'},
        {name: '27.내 차량 조회', method: 'GET', path: '/v1/users/me/cars/simple'},
        {name: '28.나의 배너 차량 조회', method: 'GET', path: '/v1/users/me/banners/car'},
        {name: '29.내차 시세 조회 기본', method: 'POST', path: '/web/myc/cc/MYCCC010303.do', params: {}},
        {name: '30.내자산 중 부동산 정보 조회', method: 'GET', path: '/v1/me/assets/real-estate'},
        {name: '31.상품별 금리 조회', method: 'GET', path: '/web/lon/hm/LONHM010301.do'},
        {name: '32.홈카드 롤링 배너 조회', method: 'GET', path: '/v1/users/me/banners', params: {bannerId: 'my-rolling'}},
        {name: '33.대출간편비교 당일 심사내역 조회', method: 'POST', path: '/web/lon/hm/LONHM010501.do', params: {acptDt: TODAY}},
        {name: '34.WEB 상품쿠폰 조회', method: 'POST', path: '/web/lon/hm/LONHM010101.do', params: {custCupnStatCd: '', cupnAplyPrdtClsfCd: ''}},
        {name: '35.계좌 목록 조회', method: 'GET', path: '/v1/me/assets/accounts'},
        {name: '36.내자산 중 연금 정보 조회', method: 'GET', path: '/v1/me/assets/pensions'},
        {name: '37.내자산 차량 정보 조회', method: 'GET', path: '/v1/me/assets/cars'},
        {name: '38.아파트 PA정보 조회', method: 'GET', path: '/web/lon/hm/LONHM010201.do'},
        {name: '39.신용대출 제휴조회', method: 'GET', path: '/web/lon/hm/LONHM010401.do'},
        {name: '40.내자산 중 기타 정보', method: 'GET', path: '/v1/me/assets/etc'},
        {name: '41.내자산 중 투자 정보 조회', method: 'GET', path: '/v1/me/assets/investments'},
        {name: '42.내자산 중 부동산 정보 조회', method: 'GET', path: '/v1/me/assets/real-estate'},
        {name: '43.대출정보 조회', method: 'GET', path: '/web/mah/li/MAHLI010101.do'},
        {name: '44.MYDATA용 CI값 존재 여부 조회', method: 'GET', path: '/web/myd/ag/MYDAG020103.do'},
        {name: '45.약관 동의 정보 조회', method: 'GET', path: '/v1/terms/auction', params: {'user-id': CUST_NO}},
        {name: '46.약관동의여부 조회', method: 'GET', path: '/web/myd/ag/MYDAG010106.do'},
        {name: '47.자산연동고객 업권별 기관연계여부 조회', method: 'POST', path: '/web/myd/cm/MYDCM010501.do', params: {}},
        {name: '48.내차 팔기 서비스 내차 정보 조회', method: 'GET', path: `/v1/users/${CUST_NO}/cars`},
        {name: '49.DSR 기등록 대출현황과 계산결과 히스토리 데이터 조회', method: 'POST', path: '/web/myd/dr/MYDDR010201.do', params: {}},
        {name: '50.자산 공통 기타 최신화 초기화 상태 조회', method: 'GET', path: '/web/myd/cm/MYDCM030301.do'},
        {name: '51.계좌 목록 조회', method: 'GET', path: '/v1/me/assets/accounts'},
        {name: '52.내자산 중 연금 정보 조회', method: 'GET', path: '/v1/me/assets/pensions'},
        {name: '53.내자산 차량 정보 조회', method: 'GET', path: '/v1/me/assets/cars'},
        {name: '54.다이렉트카 진입점 차량 정보 조회', method: 'GET', path: '/v1/direct-car/entry-point', params: {size: '10'}},
        {name: '55.내자산 중 기타 정보', method: 'GET', path: '/v1/me/assets/etc'},
        {name: '56.내자산 중 투자 정보 조회', method: 'GET', path: '/v1/me/assets/investments'},
        {name: '57.자산 공통 기타 최신화 초기화 최종수집일자 업데이트일자 조회', method: 'GET', path: '/web/myd/cm/MYDCM030401.do'},
        {name: '58.홈카드 롤링 배너 조회', method: 'GET', path: '/v1/users/me/banners', params: {bannerId: 'my-rolling'}},
        {name: '59.앱 메인 팝업 출력여부 조회', method: 'GET', path: '/web/mah/po/MAHPO010101.do'},
        {name: '60.내자산 중 부동산 정보 조회', method: 'GET', path: '/v1/me/assets/real-estate'},
        {name: '61.앱회원 특정 약관 동의여부 조회', method: 'GET', path: '/v1/users/me/terms/app-membership/status', params: { 'cust-no' : CUST_NO, terms : 'B2030'}},
        {name: '62.챗봇 플로팅 메시지 조회 API', method: 'GET', path: '/web/gcm/cb/GCMCB010101.do'},
        {name: '63.홈카드 조회', method: 'POST', path: '/v1/users/me/home-cards', params: {login: true, custNo: CUST_NO, appUuid: APP_UUID}},
    ];

    // 초기 API 호출하여 세션 ID 헤더에 설정
    const initUrl = `${BASE_URL}${initApi.path}`;
    const initBody = JSON.stringify(initApi.params);
    const initRes = http.post(initUrl, initBody, {
        headers: {
            'Content-Type': 'application/json',
            'Encryption': 'N',
        },
    });
    const cookieHeader = initRes.headers['Set-Cookie'];
    const jsessionId = cookieHeader?.match(/JSESSIONID=([^;]+)/)?.[1];

    check(jsessionId, {
        'JSESSIONID was extracted ': (v) => !!v,
    });

    const commonHeaders = {
        headers: {
            'Content-Type': 'application/json',
            'Cookie': `JSESSIONID=${jsessionId}`,
            'Encryption': 'N',
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
