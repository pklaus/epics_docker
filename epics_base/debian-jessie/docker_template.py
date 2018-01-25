#!/usr/bin/env python

# Via http://pydanny.com/jinja2-quick-load-function.html
from jinja2 import FileSystemLoader, Environment

def render_from_template(directory, template_name, **kwargs):
    loader = FileSystemLoader(directory)
    env = Environment(loader=loader)
    template = env.get_template(template_name)
    return template.render(**kwargs)

def main():
    import argparse, sys, os
    parser = argparse.ArgumentParser()
    parser.add_argument('--template-file', '-f', metavar='Dockerfile.jinja2', default='Dockerfile.jinja2', help='The Dockerfile template to use.')
    parser.add_argument('--build-config-file', '-b', default='./build_configuration.py', help='The Python file containing the build configuration.')
    subparsers = parser.add_subparsers(dest='action')
    parser_render = subparsers.add_parser('list-tags', help='Returns the list of available tags')
    parser_render = subparsers.add_parser('render', help='Render the template')
    parser_build =  subparsers.add_parser('build',  help='Render the template and build the image')
    for template_parser in parser_render, parser_build:
        template_parser.add_argument('--tag', required=True, help='The tag to build (implies the base image to derive from).')
    args = parser.parse_args()
    args.build_config_file = os.path.abspath(args.build_config_file)
    # load build_configuration.py from workdir
    import importlib.util
    spec = importlib.util.spec_from_file_location(args.build_config_file, args.build_config_file)
    build_configuration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(build_configuration)
    BUILDS = build_configuration.BUILDS
    # no action chosen
    if not args.action: parser.error("Please choose an action.")
    # list-tags
    if args.action == 'list-tags':
        for tag in BUILDS.keys(): print(tag)
        sys.exit(0)
    # render
    if args.action in ('render', 'build'):
        args.tag_end = args.tag.rpartition(':')[2]
        kwargs = BUILDS[args.tag_end]
        content = render_from_template('.', args.template_file, **kwargs)
        with open('Dockerfile', 'w') as f:
            f.write(content)
        # build
        if 'build' in args.action:
            os.system(f'docker build -t {args.tag} .')

if __name__ == "__main__": main()
