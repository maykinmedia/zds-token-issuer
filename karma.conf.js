var paths = require('./build/paths');
var webpackConfig = require('./webpack.config.js');


// The preprocessor config
var preprocessors = {};
preprocessors[paths.jsSpecEntry] = [
    'webpack',
    'coverage',
]


// The main configuration
var configuration = function(config) {
    config.set({
        frameworks: [
            'jasmine'
        ],

        plugins: [
            'karma-webpack',
            'karma-jasmine',
            'karma-coverage',
            'karma-spec-reporter',
            'karma-junit-reporter',
            'karma-chrome-launcher',
            'karma-firefox-launcher',
        ],

        files: [
            paths.jsSpecEntry
        ],

        preprocessors: preprocessors,

        webpack: webpackConfig,

        webpackMiddleware: {
            noInfo: true
        },

        reporters: ['spec', 'coverage', 'junit'],

        browsers: ['ChromiumHeadless', 'FirefoxHeadless'],

        coverageReporter: {
            reporters: [
                { type: 'text-summary' },
                { type: 'clover' },
            ],
            dir: paths.coverageDir,
        },

        junitReporter: {
            outputDir: paths.coverageDir,
            outputFile: 'test-results.xml',
            useBrowserName: false,
        },

        singleRun: true
    });
};


module.exports = configuration;
