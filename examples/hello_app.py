#!/usr/bin/env python

import json
import itertools
import jinja2

import lexington
from lexington.util.view_map import view

def jinja_loader():
    return jinja2.PackageLoader('hello_app', 'templates')

def jinja_env(loader):
    return jinja2.Environment(loader=loader)

def jinja_templates(jinja_env):
    def get_template(name):
        return jinja_env.get_template(name)
    return get_template

def template_responder(get_template, respond):
    def jinja_respond(template_name, values):
        text = get_template(template_name).render(**values)
        return respond(text, mimetype='text/html')
    return jinja_respond

def content_factory():
    n = itertools.count(1)
    def content_fn():
        return "First" + '!'*next(n)
    return content_fn

@view('index', ['content'])
def index_view(content_fn):
    return content_fn()

@view('env', ['environ'])
def show_env(environ):
    return str(environ)

@view('query', ['query'])
def show_query(query):
    return json.dumps(query)

@view('post', ['request'])
def show_post(request):
    return '{}\n{}\n'.format(request, request.form)

@view('show-name', ['request', 'jinja_respond'])
def show_name(request, jinja_respond):
    return jinja_respond('show-name.html', {
        'name': request.form.get('name'),
    })

@view('set-name', ['jinja_respond'])
def set_name(jinja_respond):
    return jinja_respond('set-name.html', {})

def create_app():
    builder = lexington.app()

    builder.add_factory('jinja_loader', jinja_loader, [])
    builder.add_factory('jinja_env', jinja_env, ['jinja_loader'])
    builder.add_factory('get_template', jinja_templates, ['jinja_env'])
    builder.add_factory('jinja_respond', template_responder, ['get_template', 'respond'])
    builder.add_value('content', content_factory())

    builder.add_route('index', 'GET', '/')
    builder.add_view(index_view)

    builder.add_route('env', 'GET', '/env')
    builder.add_view(show_env)

    builder.add_route('query', 'GET', '/query')
    builder.add_view(show_query)

    builder.add_route('no_view', 'GET', '/no-view')

    builder.add_route('post', 'POST', '/post')
    builder.add_view(show_post)

    builder.add_route('show-name', 'POST', '/hello')
    builder.add_view(show_name)
    builder.add_route('set-name', 'GET', '/hello')
    builder.add_view(set_name)

    return builder.create_app()

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    app = create_app()
    run_simple('localhost', 5050, app, use_debugger=True, use_reloader=True)
