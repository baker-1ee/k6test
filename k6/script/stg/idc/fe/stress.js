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
    'https://stg-app2v.hyundaicapital.com/spa-root/assets/js/vconsole.min.js',
    'https://stg-app2v.hyundaicapital.com/spa-root/main/R32123/remoteEntry.js',
    'https://stg-app2v.hyundaicapital.com/rent/R10181/remoteEntry.js?t=ig2g5pza',
    'https://stg-app2v.hyundaicapital.com/spa-root/main/R32123/css/src_bootstrap_ts.f57675b5517b02bb.css',
    'https://stg-app2v.hyundaicapital.com/spa-root/main/R32123/js/src_bootstrap_ts.e573901f8889d138.js',
    'https://stg-app2v.hyundaicapital.com/rent/R10181/js/modules_mapp_node_modules_vue-class-component_dist_vue-class-component_esm_js.4a2ef6338a2290ae.js',
    'https://stg-app2v.hyundaicapital.com/rent/R10181/js/modules_mapp_node_modules_vue-property-decorator_lib_index_js.c0224efa19cb8a1f.js',
    'https://stg-app2v.hyundaicapital.com/rent/R10181/js/modules_mapp_node_modules_vuex-class_lib_index_js.f529826383680353.js',
    'https://stg-app2v.hyundaicapital.com/rent/R10181/js/modules_mapp_node_modules_body-scroll-lock_lib_bodyScrollLock_esm_js.daaf291b7dacb11d.js',
    'https://stg-app2v.hyundaicapital.com/rent/R10181/js/modules_mapp_node_modules_axios_index_js.d4b3d6fba18bfc71.js',
    'https://stg-app2v.hyundaicapital.com/rent/R10181/js/modules_mapp_node_modules_dayjs_dayjs_min_js.63545518dbc962f6.js',
    'https://stg-app2v.hyundaicapital.com/spa-root/main/R32123/js/modules_mapp-terminal_node_modules_holiday-kr_index_js.9922f4af8510f954.js',
    'https://stg-app2v.hyundaicapital.com/rent/R10181/js/modules_mapp_node_modules_lodash-es_lodash_js.a7e65e5c621df4b0.js',
    'https://stg-app2v.hyundaicapital.com/spa-root/main/R32123/js/modules_mapp-terminal_node_modules_swiper_swiper_mjs.a938436896914dc5.js',
    'https://stg-app2v.hyundaicapital.com/spa-root/main/R32123/js/modules_mapp-terminal_node_modules_smoothscroll-polyfill_dist_smoothscroll_js.cd8d4fd00130dd25.js',
    'https://stg-app2v.hyundaicapital.com/rent/R10181/js/modules_mapp_node_modules_vuetify_dist_vuetify_js.731e022e70d2df47.js',
    'https://stg-app2v.hyundaicapital.com/rent/R10181/js/modules_mapp_node_modules_vue-observe-visibility_dist_vue-observe-visibility_esm_js.08f92ac0d6de0daa.js',
    'https://stg-app2v.hyundaicapital.com/rent/R10181/js/modules_mapp_node_modules_elastic_apm-rum-vue_dist_es_index_js.5a4383cb05ae6954.js',
    'https://stg-app2v.hyundaicapital.com/spa-root/main/R32123/js/modules_mapp-terminal_node_modules_chart_js_dist_chart_mjs.3c768e8997e34cbd.js',
    'https://stg-app2v.hyundaicapital.com/spa-root/main/R32123/js/modules_mapp-terminal_node_modules_vue-chartjs_dist_index_js.986c43bd8fc6baa0.js',
    'https://stg-app2v.hyundaicapital.com/spa-root/main/R32123/js/modules_mapp-terminal_node_modules_chartjs-plugin-datalabels_dist_chartjs-plugin-datalabels_esm_js.7e878626864c9979.js',
    'https://stg-app2v.hyundaicapital.com/rent/R10181/js/src_router_index_ts.afeeb76990acc72c.js',
    'https://stg-app2v.hyundaicapital.com/rent/R10181/js/src_api_url_ts.7a2bf68e68181323.js',
    'https://stg-app2v.hyundaicapital.com/rent/R10181/js/src_domain_direct_store_actionConstructor_ts.a8c025527e03798e.js',
    'https://stg-app2v.hyundaicapital.com/rent/R10181/js/src_domain_direct_const_common_constants_ts.55071de66dc5f576.js',
    'https://stg-app2v.hyundaicapital.com/rent/R10181/js/src_domain_direct_store_getters_ts.0e28c20eafac498e.js',
    'https://stg-app2v.hyundaicapital.com/rent/R10181/js/src_mixins_WebChatbotMixin_ts.df690edfb423c310.js',
    'https://stg-app2v.hyundaicapital.com/rent/R10181/js/src_domain_direct_store_state_ts.b4deb0a90e72bcda.js',
    'https://stg-app2v.hyundaicapital.com/rent/R10181/js/src_domain_direct_store_mutations_ts.314c116ce925f3c0.js',
    'https://stg-app2v.hyundaicapital.com/rent/R10181/js/src_domain_multi-cycle_store_state_ts.a9b9928b554fce4b.js',
    'https://stg-app2v.hyundaicapital.com/rent/R10181/js/src_domain_multi-cycle_store_getters_ts.0c86d522b02da2c1.js',
    'https://stg-app2v.hyundaicapital.com/rent/R10181/js/src_domain_multi-cycle_store_mutations_ts.74c54f9ebd5b39fd.js',
    'https://stg-app2v.hyundaicapital.com/rent/R10181/js/src_domain_multi-cycle_store_actionConstructor_ts.f317c00c6c9f7f0e.js',
    'https://stg-app2v.hyundaicapital.com/spa-root/main/R32123/js/src_app_store_helper_ts.50fdff222d45e6b5.js',
    'https://stg-app2v.hyundaicapital.com/spa-root/main/R32123/js/src_app_utils_converter_index_ts-src_app_utils_logger_index_ts-src_app_utils_system_index_ts.ef00788cf58f1403.js',
    'https://stg-app2v.hyundaicapital.com/rent/R10181/js/modules_mapp_node_modules_swiper_js_swiper_esm_bundle_js.1e0f244e147df1cb.js',
    'https://stg-app2v.hyundaicapital.com/rent/R10181/js/modules_mapp_node_modules_vue-awesome-swiper_dist_vue-awesome-swiper_js.25b270395a93a05e.js',
    'https://stg-app2v.hyundaicapital.com/spa-root/main/R32123/css/capital-hub.6b562b43efa40a3a.css',
    'https://stg-app2v.hyundaicapital.com/spa-root/main/R32123/js/capital-hub.d54b9edbd78bd287.js',
    'https://stg-app2v.hyundaicapital.com/rent/R10181/js/src_domain_direct_const_rental-option_constants_ts.e45cbe73877eb8ac.js',
    'https://stg-app2v.hyundaicapital.com/rent/R10181/css/src_components_buttons_ChatbotButton_vue.a433da69c616194f.css',
    'https://stg-app2v.hyundaicapital.com/rent/R10181/js/src_components_buttons_ChatbotButton_vue.e71a0cb5a1eb7c61.js',
    'https://stg-app2v.hyundaicapital.com/spa-root/main/R32123/js/src_app_modules_js-interface_chatbot-js-interface_types_ts.44da13ec53454f02.js',
    'https://stg-app2v.hyundaicapital.com/spa-root/main/R32123/js/src_app_mixins_LifeCycleMixins_CommonTaggingMixin_ts.501b002e6260d3fc.js',
    'https://stg-app2v.hyundaicapital.com/spa-root/main/R32123/css/capital-menu-entry.4a8eb24658508bdc.css',
    'https://stg-app2v.hyundaicapital.com/spa-root/main/R32123/js/capital-menu-entry.efab9ae82639b4c8.js',
    'https://stg-app2v.hyundaicapital.com/spa-root/main/R32123/css/capital-wishlist.64066690639ccd10.css',
    'https://stg-app2v.hyundaicapital.com/spa-root/main/R32123/js/capital-wishlist.705b3713fd89e832.js',
    'https://stg-app2v.hyundaicapital.com/spa-root/main/R32123/css/capital-etc.e667b584b2ff1b30.css',
    'https://stg-app2v.hyundaicapital.com/spa-root/main/R32123/js/capital-etc.eda79f757c3013b6.js',
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
