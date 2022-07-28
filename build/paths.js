var path = require('path');
var fs = require('fs');


/** Parses package.json */
var pkg = JSON.parse(fs.readFileSync('./package.json', 'utf-8'));

/** Name of the sources directory */
var sourcesRoot = 'src/' + pkg.name + '/';

/** Name of the static (source) directory */
var staticRoot = sourcesRoot + 'static/';


/**
 * Application path configuration for use in frontend scripts
 */
module.exports = {
    // Parsed package.json
    package: pkg,

    // Path to the sass (sources) directory
    sassSrcDir: sourcesRoot + 'sass/',

    // Path to the sass entry point
    sassEntry: sourcesRoot + 'sass/screen.scss',

    // Path to the (transpiled) css directory
    cssDir: staticRoot + 'css/',

    // Path to the fonts directory
    fontsDir: staticRoot + 'fonts/',

    // Path to the js entry point (source)
    jsEntry: sourcesRoot + 'js/index.js',

    // Path to the (transpiled) js directory
    jsDir: staticRoot + 'bundles/',

    // Path to js spec (test) files
    jsSpec: sourcesRoot + 'jstests/**/*.spec.js',

    // Path to js spec (test) entry file
    jsSpecEntry: sourcesRoot + 'jstests/index.js',

    // Path to js code coverage directory
    coverageDir: 'reports/jstests/',
};
