# -*- coding: utf-8 -*-

import sys
import os, os.path
import glob
import fnmatch
import pprint

try:
    from myterm.parser import OptionParser
except:
    from optparse import OptionParser    

from piwigotools import Piwigo, __version__
from piwigo.ws import Ws
from piwigotools.interface import *

DESCRIPTION = "tools for piwigo gallery"
USAGE = """piwigo verb --param1=value1 --param2=value2
verb list
- upload
- download
- sync-up
- sync-down
- ws

to get help: piwigo verb --help
"""
AUTHOR = "Frederic Aoustin"
PROG = "piwigo"
VERSION = __version__

VERBS = {
        "upload":
            { 
                "usage" : "usage for verb upload",
                "description" : "upload file in piwigo gallery",
                "arg" : 
                    {
                        "category" : {"type":"string", "default":"", "help":"destination category of piwigo gallery"},
                        "source" : {"type":"string", "default":"*.jpg", "help":"path of upload picture"},
                        "url" :  {"type":"string", "default":"", "help":"url of piwigo gallery"},
                        "user" :  {"type":"string", "default":"", "help":"user of piwigo gallery"},
                        "password" :  {"type":"string", "default":"", "help":"password of piwigo gallery"},
                        "thread" :  {"type":"int", "default":"1", "help":"number of thread"},
                    },
            },
        "download":
            { 
                "usage" : "usage for verb download",
                "description" : "download image from piwigo gallery",
                "arg" : 
                    {
                        "category" : {"type":"string", "default":"", "help":"source category of piwigo gallery"},
                        "dest" : {"type":"string", "default":".", "help":"path of destination"},
                        "url" :  {"type":"string", "default":"", "help":"url of piwigo gallery"},
                        "user" :  {"type":"string", "default":"", "help":"user of piwigo gallery"},
                        "password" :  {"type":"string", "default":"", "help":"password of piwigo gallery"},
                        "thread" :  {"type":"int", "default":"1", "help":"number of thread"},
                    },
            },
        "sync-up":
            { 
                "usage" : "usage for verb sync-up",
                "description" : "synchronization local path to piwigo gallery",
                "arg" : 
                    {
                        "category" : {"type":"string", "default":"", "help":"category of piwigo gallery"},
                        "source" : {"type":"string", "default":".", "help":"path of picture"},
                        "url" :  {"type":"string", "default":"", "help":"url of piwigo gallery"},
                        "user" :  {"type":"string", "default":"", "help":"user of piwigo gallery"},
                        "password" :  {"type":"string", "default":"", "help":"password of piwigo gallery"},
                        "thread" :  {"type":"int", "default":"1", "help":"number of thread"},
                        "extension" :  {"type":"string", "default":"*.JPG,*.jpg,*.PNG,*.png,*.JPEG,*.jpeg,*.GIF,*.gif", "help":"extension for upload"},
                    },
            },
       "sync-down":
            { 
                "usage" : "usage for verb sync-down",
                "description" : "synchronization piwigo gallery to local path",
                "arg" : 
                    {
                        "category" : {"type":"string", "default":"", "help":"category of piwigo gallery"},
                        "source" : {"type":"string", "default":".", "help":"path of picture"},
                        "url" :  {"type":"string", "default":"", "help":"url of piwigo gallery"},
                        "user" :  {"type":"string", "default":"", "help":"user of piwigo gallery"},
                        "password" :  {"type":"string", "default":"", "help":"password of piwigo gallery"},
                        "thread" :  {"type":"int", "default":"1", "help":"number of thread"},
                        "extension" :  {"type":"string", "default":"*.JPG,*.jpg,*.PNG,*.png,*.JPEG,*.jpeg,*.GIF,*.gif", "help":"extension for upload"},
                    },
            },
         "ws":
            { 
                "usage" : "usage for verb ws",
                "description" : "use web service of piwigo gallery",
                "arg" : 
                    {
                        "method" : {"type":"string", "default":".", "help":"name of web service"},
                        "url" :  {"type":"string", "default":"", "help":"url of piwigo gallery"},
                    },
            },
 
        }

def add_dynamic_option(parser):
    
    # add arg for verb
    if not len(sys.argv) > 1:
        parser.print_help()
        sys.exit(1)
    
    if sys.argv[1] in ("--help", "-h"):
        parser.print_help()
        parser.print_version()
        sys.exit(0)
 
    if sys.argv[1] in ("--version"):
        parser.print_version()
        sys.exit(0)
        
    
    verb = sys.argv[1]
    arg_know = ['--help']
    for arg in VERBS.get(verb, {'arg':{}})['arg']:
        kw = VERBS[sys.argv[1]]['arg'][arg]
        kw['dest'] = arg
        parser.add_option("--%s" % arg, **kw)
        arg_know.append("--%s" % arg)
    # add arg in argv
    for arg in sys.argv[2:]:
        if arg[:2] == '--' and arg.split('=')[0] not in arg_know:
            arg = arg[2:].split('=')[0]
            parser.add_option("--%s" % arg , dest=arg, type="string")
            arg_know.append("--%s" % arg)


    #check verb
    if verb not in VERBS:
        parser.print_help()
        parser.exit(status=2, msg='verb "%s" unknow\n' % verb)
        sys.exit(0)

    parser.set_usage(VERBS[verb]["usage"])
    parser.description = VERBS[verb]["description"]

    if '--help' in sys.argv[1:]:
        parser.print_help()
        sys.exit(0)



def main():
    usage = USAGE
    parser = OptionParser(version="%s %s" % (PROG,VERSION), usage=usage)
    parser.description= DESCRIPTION
    parser.epilog = AUTHOR
    try:
        add_dynamic_option(parser)
        (options, args) = parser.parse_args()
        verb = args[0]
        if verb == 'ws':
            piwigo = Piwigo(url=options.url)
            if 'user' and 'password' in options.__dict__:
                piwigo.login(options.user, options.password)
            kw = purge_kw(options.__dict__,('user','password','url'))
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(Ws(piwigo, options.method)(**kw))
            if piwigo.islogged:
                piwigo.logout()
        if verb == "download":
            ana = Analyse('Analyze')
            ana.start()
            try:
                piwigo = Piwigo(url=options.url)
                piwigo.login(options.user, options.password)
                # check
                if not os.path.isdir(options.dest):
                    os.makedirs(options.dest)        
                options.dest = os.path.abspath(options.dest)
                piwigo.iscategory(options.category)
                if options.category[-2:] == ' /' : options.category = options.category[:-2]
                # treatment
                run = Run(verb, options.thread)
                kw = purge_kw(options.__dict__,('user','password','url','dest','category','thread'))
                for img in piwigo.images(options.category, **kw):
                    run.add(piwigo.download, 
                            ["%s / %s" % (options.category, str(img)), "%s%s%s" % (options.dest, os.path.sep, str(img))],
                            kw)
            except Exception as e:
                ana.stop()
                raise e
            ana.stop()
            run.start()
            piwigo.logout()
            if run.error:
               parser.error(run.strerror) 
        if verb == "upload":
            ana = Analyse('Analyze')
            ana.start()
            try:
                piwigo = Piwigo(url=options.url)
                piwigo.login(options.user, options.password)
                # check
                piwigo.makedirs(options.category)
                # treatment
                run = Run(verb, options.thread)
                kw = purge_kw(options.__dict__,('user','password','url','source','category','thread'))
                for img in glob.glob(options.source):
                    run.add(piwigo.upload,
                            [os.path.abspath(img), options.category], 
                            kw)
                ana.stop()
            except Exception as e:
                ana.stop()
                raise e
            run.start()
            piwigo.logout()
            if run.error:
                parser.error(run.strerror)
        if verb == "sync-up":
            ana = Analyse('Analyze')
            ana.start()
            try:
                piwigo = Piwigo(url=options.url)
                piwigo.login(options.user, options.password)
                # check
                options.source = os.path.abspath(options.source)
                if not os.path.isdir(options.source):
                    raise Exception("%s is not directory" % options.source)
                piwigo.iscategory(options.category)
                if len(options.category) and options.category[-1] != '/' and options.category[:-3] != ' / ':
                    options.category = options.category+ ' / '
                # treatment
                run = Run(verb, options.thread)
                kw = purge_kw(options.__dict__,('user','password','url','source','category','thread'))
                # local -> piwigo
                for root, dirnames, filenames in os.walk(options.source):
                    filtering = fnmatch.filter(filenames, options.extension.split(',')[0])
                    for ext in options.extension.split(',')[1:]:
                        filtering = filtering + fnmatch.filter(filenames, ext)
                    for filename in filtering:
                        pathrel = os.path.abspath(os.path.join(root, filename))[len(options.source)+1:]
                        pathabs = os.path.abspath(os.path.join(root, filename))
                        category = options.category + ' / '.join(pathrel.split(os.sep)[:-1])
                        if not piwigo.isimage(category + ' / ' + filename):
                            run.add(piwigo.makedirs,[category,], kw)
                            run.add(piwigo.upload,[pathabs, category], kw)
                ana.stop()
            except Exception as e:
                ana.stop()
                raise e
            run.start()
            piwigo.logout()
            if run.error:
                parser.error(run.strerror)
        if verb == "sync-down":
            ana = Analyse('Analyze')
            ana.start()
            try:
                piwigo = Piwigo(url=options.url)
                piwigo.login(options.user, options.password)
                # check
                options.source = os.path.abspath(options.source)
                if not os.path.isdir(options.source):
                    raise Exception("%s is not directory" % options.source)
                piwigo.iscategory(options.category)
                if len(options.category) and options.category[-1] != '/' and options.category[:-3] != ' / ':
                    options.category = options.category+ ' / '
                # treatment
                run = Run(verb, options.thread)
                kw = purge_kw(options.__dict__,('user','password','url','source','category','thread'))
                # piwigo -> local
                for category, item in piwigo.plan.iteritems():
                    if options.category == category[0:len(options.category)]:
                        path = os.path.join(options.source, *category[len(options.category):].split(' / '))
                        if not os.path.exists(path):
                            os.makedirs(path)
                        for img in piwigo.images(category):
                            pathimg = os.path.join(path, img)
                            if not os.path.exists(pathimg):
                                run.add(piwigo.download, 
                                    ["%s / %s" % (category, str(img)), pathimg],
                                    kw)
                ana.stop()
            except Exception as e:
                ana.stop()
                raise e
            run.start()
            piwigo.logout()
            if run.error:
                parser.error(run.strerror)
    except Exception as e:
        parser.error(e)
        sys.exit(1)

if __name__ == "__main__":
    main()

