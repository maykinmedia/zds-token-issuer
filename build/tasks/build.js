const gulp = require('gulp');
const { scss } = require('./scss');
const { js } = require('./js');

const build = gulp.parallel(scss, js);

gulp.task('build', build);
exports.build = build;
