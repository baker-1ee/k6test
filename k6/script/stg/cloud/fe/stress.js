import http from 'k6/http';
import { sleep, check } from 'k6';
import { Trend } from 'k6/metrics';

let ttfb = new Trend('a_ttfb', true);
let download = new Trend('b_download_time', true);
let total = new Trend('c_total_duration', true);

export let options = {
    stages: [
        { duration: '5m', target: 50 },
        { duration: '5m', target: 100 },
        { duration: '5m', target: 150 },
        { duration: '5m', target: 200 },
        { duration: '5m', target: 0 },
    ],
};

const urls = [
    'https://stg-app.hyundaicapital.com/spa-root/assets/js/vconsole.min.js',
    'https://d1skruajn39z13.cloudfront.net/spa-root/main/R32117/remoteEntry.js',
    'https://stg-app.hyundaicapital.com/rent/R10171/remoteEntry.js?t=dbki2wfk',
    'https://d1skruajn39z13.cloudfront.net/spa-root/main/R32117/css/src_bootstrap_ts.2e23930705a40b90.css',
    'https://d1skruajn39z13.cloudfront.net/spa-root/main/R32117/js/src_bootstrap_ts.7e7acc4a7fd6dd8a.js',
    'https://stg-app.hyundaicapital.com/rent/R10171/js/node_modules_vue-class-component_dist_vue-class-component_esm_js.4fdad0b6b295bf2b.js',
    'https://stg-app.hyundaicapital.com/rent/R10171/js/node_modules_vue-property-decorator_lib_index_js.201e5da371739766.js',
    'https://stg-app.hyundaicapital.com/rent/R10171/js/node_modules_vuex-class_lib_index_js.bf0b13cdc41d5cb5.js',
    'https://stg-app.hyundaicapital.com/rent/R10171/js/node_modules_body-scroll-lock_lib_bodyScrollLock_esm_js.9e4b65454f5c1a0b.js',
    'https://stg-app.hyundaicapital.com/rent/R10171/js/node_modules_axios_index_js.57ed689b24b180a7.js',
    'https://stg-app.hyundaicapital.com/rent/R10171/js/node_modules_dayjs_dayjs_min_js.e03d90cfdab987ad.js',
    'https://d1skruajn39z13.cloudfront.net/spa-root/main/R32117/js/node_modules_holiday-kr_index_js.9e1398a902346a35.js',
    'https://stg-app.hyundaicapital.com/rent/R10171/js/node_modules_lodash-es_lodash_js.8c6c1d3840151a72.js',
    'https://d1skruajn39z13.cloudfront.net/spa-root/main/R32117/js/node_modules_swiper_swiper_mjs.aeefb9007bd1c3c0.js',
    'https://d1skruajn39z13.cloudfront.net/spa-root/main/R32117/js/node_modules_smoothscroll-polyfill_dist_smoothscroll_js.696bdf9bb87c6b86.js',
    'https://stg-app.hyundaicapital.com/rent/R10171/js/node_modules_vuetify_dist_vuetify_js.c923b5895fc0b3e1.js',
    'https://stg-app.hyundaicapital.com/rent/R10171/js/node_modules_vue-observe-visibility_dist_vue-observe-visibility_esm_js.ab24b48414641012.js',
    'https://stg-app.hyundaicapital.com/rent/R10171/js/node_modules_elastic_apm-rum-vue_dist_es_index_js.612a768a61d3174a.js',
    'https://d1skruajn39z13.cloudfront.net/spa-root/main/R32117/js/node_modules_chart_js_dist_chart_mjs.edd9597866c164ab.js',
    'https://d1skruajn39z13.cloudfront.net/spa-root/main/R32117/js/node_modules_vue-chartjs_dist_index_js.5c3aeb55ee46b899.js',
    'https://d1skruajn39z13.cloudfront.net/spa-root/main/R32117/js/node_modules_chartjs-plugin-datalabels_dist_chartjs-plugin-datalabels_esm_js.6e0f333e4aaf2aa0.js',
    'https://stg-app.hyundaicapital.com/rent/R10171/js/src_router_index_ts.afeeb76990acc72c.js',
    'https://stg-app.hyundaicapital.com/rent/R10171/js/src_api_url_ts.7a2bf68e68181323.js',
    'https://stg-app.hyundaicapital.com/rent/R10171/js/src_domain_direct_store_actionConstructor_ts.b492c4c61d83560a.js',
    'https://stg-app.hyundaicapital.com/rent/R10171/js/src_domain_direct_const_common_constants_ts.55071de66dc5f576.js',
    'https://stg-app.hyundaicapital.com/rent/R10171/js/src_domain_direct_store_getters_ts.0e28c20eafac498e.js',
    'https://stg-app.hyundaicapital.com/rent/R10171/js/src_mixins_WebChatbotMixin_ts.b2e1666ac4457495.js',
    'https://stg-app.hyundaicapital.com/rent/R10171/js/src_domain_direct_store_state_ts.b4deb0a90e72bcda.js',
    'https://stg-app.hyundaicapital.com/rent/R10171/js/src_domain_direct_store_mutations_ts.dc24b427a793e6ff.js',
    'https://stg-app.hyundaicapital.com/rent/R10171/js/src_domain_multi-cycle_store_state_ts.a9b9928b554fce4b.js',
    'https://stg-app.hyundaicapital.com/rent/R10171/js/src_domain_multi-cycle_store_getters_ts.0c86d522b02da2c1.js',
    'https://stg-app.hyundaicapital.com/rent/R10171/js/src_domain_multi-cycle_store_mutations_ts.4ec78264d934b017.js',
    'https://stg-app.hyundaicapital.com/rent/R10171/js/src_domain_multi-cycle_store_actionConstructor_ts.788e71fdb7268350.js',
    'https://d1skruajn39z13.cloudfront.net/spa-root/main/R32117/js/src_app_store_helper_ts.2cfde1ce78e6f6b3.js',
    'https://d1skruajn39z13.cloudfront.net/spa-root/main/R32117/js/src_app_utils_converter_index_ts-src_app_utils_logger_index_ts-src_app_utils_system_index_ts.59c9d78af383d83d.js',
    'https://stg-app.hyundaicapital.com/rent/R10171/js/node_modules_swiper_js_swiper_esm_bundle_js.ef87cfdf2122e412.js',
    'https://stg-app.hyundaicapital.com/rent/R10171/js/node_modules_vue-awesome-swiper_dist_vue-awesome-swiper_js.1c41f7141cbc1f03.js',
    'https://d1skruajn39z13.cloudfront.net/spa-root/main/R32117/css/capital-hub.8790e82c1141eada.css',
    'https://d1skruajn39z13.cloudfront.net/spa-root/main/R32117/js/capital-hub.b68f1e3fbcc6eb2e.js',
    'https://stg-app.hyundaicapital.com/rent/R10171/js/src_domain_direct_const_rental-option_constants_ts.e45cbe73877eb8ac.js',
    'https://stg-app.hyundaicapital.com/rent/R10171/css/src_components_buttons_ChatbotButton_vue.a433da69c616194f.css',
    'https://stg-app.hyundaicapital.com/rent/R10171/js/src_components_buttons_ChatbotButton_vue.5f86368cfbecc47c.js',
    'https://d1skruajn39z13.cloudfront.net/spa-root/main/R32117/js/src_app_modules_js-interface_chatbot-js-interface_types_ts.44da13ec53454f02.js',
    'https://d1skruajn39z13.cloudfront.net/spa-root/main/R32117/js/src_app_mixins_LifeCycleMixins_CommonTaggingMixin_ts.77e5099b88cdfd8f.js',
    'https://d1skruajn39z13.cloudfront.net/spa-root/main/R32117/css/capital-menu-entry.4a8eb24658508bdc.css',
    'https://d1skruajn39z13.cloudfront.net/spa-root/main/R32117/js/capital-menu-entry.3618b1a906fe5c12.js',
    'https://d1skruajn39z13.cloudfront.net/spa-root/main/R32117/css/capital-wishlist.64066690639ccd10.css',
    'https://d1skruajn39z13.cloudfront.net/spa-root/main/R32117/js/capital-wishlist.86ca88a017365615.js',
    'https://d1skruajn39z13.cloudfront.net/spa-root/main/R32117/css/capital-etc.e667b584b2ff1b30.css',
    'https://d1skruajn39z13.cloudfront.net/spa-root/main/R32117/js/capital-etc.da941a7d7ebf8f04.js',
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
    sleep(0.2);
}
