#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Module piwigotools
"""

__version_info__ = (0, 0, 2)
__version__ = '.'.join([str(val) for val in  __version_info__])

import inspect

import requests

import piwigo

class LoginException(Exception):

    def __str__(self):
        return "You are not logged"

class PiwigoException(Exception):
    
    def __init__(self, strerr):
        self._strerr = strerr

    def __str__(self):
        return self._strerr

class PiwigoExistException(PiwigoException):
    
    def __init__(self, strerr):
        PiwigoException.__init__(self, strerr)


class Piwigo(piwigo.Piwigo):
    """
        describe piwigo gallery
    """

    def __init__(self, url):
        piwigo.Piwigo.__init__(self, url)
        self._login = False

    def login(self, username, password):
        """
            login on piwigo gallery
        """
        self.pwg.session.login(username=username, password=password)
        self._login = True
        return True

    def logout(self):
        """
            logout on piwigo gallery
        """
        self.pwg.session.logout()
        self._login = False
        return True

    @property
    def plan(self):
        plan = { i["name"] : i["id"] for i in self.pwg.categories.getList(recursive=True, fullname=True)['categories'] }
        plan[""] = 0
        return plan

    def _checkarg(fn):
        def checking(self, *args, **kw):
            args = list(args)
            # manage path
            if inspect.getargspec(fn).args.count('path'): 
                pos = inspect.getargspec(fn).args.index('path') -1
                if args[pos][-2:] == ' /' : args[pos] = args[pos][:-2]
            args = tuple(args)
            return fn(self, *args, **kw)
        return checking    
 
    def _checklogin(fn):
        def checking(self, *args, **kw):
            if self._login:
                return fn(self, *args, **kw)
            raise LoginException()
        return checking    
 
    @property
    @_checklogin
    def token(self):
        """
            return pwg_token
        """
        return self.pwg.session.getStatus()["pwg_token"]

    def islogged(self):
        try:
            self.token
        except LoginException: 
            return False
        return True

    @_checkarg
    def iscategory(self, path):
        if path in self.plan:
            return True
        return False

    @_checkarg
    def idcategory(self, path):
        if not self.iscategory(path):
            raise PiwigoExistException("category %s not exist" % path)
        return self.plan[path]
   
    @_checkarg
    def images(self, path, **kw):
        """
            return list of file name image for path
        """
        try:
            kw["cat_id"]= self.idcategory(path)
        except PiwigoExistException:
            return {}
        kw["per_page"] = 200
        kw["page"] = 0
        imgs = {}
        loop = True
        while loop:
            req = self.pwg.categories.getImages(**kw)
            for img in req["images"]:
                imgs[img["file"]] = img
            if req["paging"]["count"] < req["paging"]["per_page"]:
                loop = False
        return imgs

    @_checkarg
    def sublevels(self, path, **kw):
        """
            return list of category in for path
        """
        kw["cat_id"]= self.idcategory(path)
        return  { i["name"] : i for i in self.pwg.categories.getList(**kw)['categories'] if i["id"] != kw["cat_id"] }


    @_checkarg
    def isimage(self, path):
        img = path.split(' / ')[-1]
        path =  ' / '.join(path.split(' / ')[:-1])
        if img in self.images(path):
            return True
        return False
    
    @_checkarg
    def idimage(self, path):
        if not self.isimage(path):
            raise PiwigoExistException("image %s not exist" % path)
        img = path.split(' / ')[-1]
        path =  ' / '.join(path.split(' / ')[:-1])
        return self.images(path)[img]["id"]

    @_checkarg
    @_checklogin
    def mkdir(self, path, **kw):
        """
            create a category named path
        """
        kw['name'] = path.split(' / ')[-1]
        parent = ' / '.join(path.split(' / ')[:-1])
        if parent and not self.iscategory(parent):
            raise PiwigoExistException("category %s not exist" % parent)
        if parent : kw['parent'] = self.plan[parent]
        self.pwg.categories.add(**kw)
        return self.idcategory(path)

    @_checkarg
    @_checklogin
    def makedirs(self, path, **kw):
        """
            recursive category create function
        """
        pp = ''
        for p in path.split(' / '):
            pp = '%s%s' % (pp, p)
            if not self.iscategory(pp):
                self.mkdir(pp, **kw)
            pp = '%s / ' % pp
        return self.idcategory(path)

    @_checkarg
    @_checklogin
    def removedirs(self, path, **kw):
        """
            remove (delete) category
        """
        self.pwg.categories.delete(category_id=self.idcategory(path), pwg_token=self.token, **kw)
        return True

    @_checkarg
    @_checklogin
    def upload(self, image, path="", **kw):
        """
            upload image in path
        """
        kw["image"] = image
        if len(path):
            if not self.iscategory(path):
                raise PiwigoExistException("category %s not exist" % parent)
            kw['category'] = self.idcategory(path)
        return self.pwg.images.addSimple(**kw)['image_id']

    @_checkarg
    @_checklogin
    def download(self, path, dst, **kw):
        """
            download image dst
        """
        if not self.isimage(path):
            raise PiwigoException("image %s not exist" % path)
        img = path.split(' / ')[-1]
        path =  ' / '.join(path.split(' / ')[:-1])
        url = self.images(path)[img]['element_url']
        with open(dst, 'wb') as img:
            r = requests.get(url)
            img.write(r.content)
            r.connection.close()
        return True


    @_checklogin
    def remove(self, path, **kw):
        """
            remove (delete) image
        """
        if not self.isimage(path):
            raise PiwigoException("image %s not exist" % path)
        self.pwg.images.delete(image_id= self.idimage(path), pwg_token=self.token)
        return True
