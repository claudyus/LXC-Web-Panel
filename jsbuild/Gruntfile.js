'use strict';

module.exports = function(grunt) {

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),

        concat: {
            js: {
                src: [
                    'bower_components/jquery/jquery.js',
                    'bower_components/bootstrap/bootstrap/js/bootstrap.js',
                    'bower_components/bootstrap-switch/build/js/bootstrap-switch.js',
                    'bower_components/jqBootstrapValidation/dist/jqBootstrapValidation-1.3.7.js'
                ],
                dest: '../lwp/static/js/bootstrap.js'
            },
            css: {
                src: [
                    'bower_components/bootstrap/bootstrap/css/bootstrap.css',
                    'bower_components/bootstrap/bootstrap/css/bootstrap-responsive.css',
                    'bower_components/bootstrap-switch/build/css/bootstrap2/bootstrap-switch.css'
                ],
                dest: '../lwp/static/css/bootstrap.css'
            }
        },

        uglify: {
            compress: {
                files: {
                    '../lwp/static/js/bootstrap.min.js': ['../lwp/static/js/bootstrap.js']
                },
                options: {
                    mangle: true
                }
            }
        },

        cssmin: {
            build: {
                src: '../lwp/static/css/bootstrap.css',
                dest: '../lwp/static/css/bootstrap.min.css'
            }
        },

        copy: {
          main: {
            expand: true,
            cwd: 'bower_components/bootstrap/',
            src: 'img/*',
            dest: '../lwp/static/img/',
            flatten: true,
            filter: 'isFile',
          },
        }
    });

    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-cssmin');

    grunt.registerTask('default', ['concat', 'uglify', 'cssmin', 'copy']);
};
