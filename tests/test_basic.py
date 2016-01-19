#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Basic Test Case
"""

import unittest
import os
import os.path

from piwigotools import Piwigo, LoginException, PiwigoExistException

class BasicTestCase(unittest.TestCase):
    """
        Class for Basic Test for piwigotools
    """
    def setUp(self):
        self.url = "http://mygallery.piwigo.com/"
        self.usertest = 'USERTEST'
        self.passwordtest = 'xxxxxx'
        self.piwigo = Piwigo(self.url)

    def test_basic(self):
        self.assertTrue(self.piwigo.pwg.getVersion())
    
    def test_checkLogin(self):
        self.assertTrue(self.piwigo.login(self.usertest, self.passwordtest))
        self.assertTrue(self.piwigo.logout())
        self.assertRaises(LoginException, self.piwigo.mkdir)
        self.assertRaises(LoginException, self.piwigo.makedirs)
        self.assertRaises(LoginException, self.piwigo.upload)

    def test_createCategory(self):
        self.piwigo.login(self.usertest, self.passwordtest)
        self.assertTrue(self.piwigo.mkdir('/level'))
        self.assertTrue(self.piwigo.mkdir('/level/sublevel'))
        self.assertTrue(self.piwigo.makedirs('/level2/sublevel2'))
        self.piwigo.removedirs('/level2')
        self.piwigo.removedirs('/level')
        self.piwigo.logout()

    def test_checkpath(self):
        self.piwigo.login(self.usertest, self.passwordtest)
        self.piwigo.mkdir('/level')
        self.assertTrue(self.piwigo.iscategory('/level'))
        self.assertTrue(self.piwigo.iscategory('/level/'))
        self.piwigo.removedirs('/level')
        self.piwigo.logout()

    def test_removeCategory(self):
        self.piwigo.login(self.usertest, self.passwordtest)
        self.piwigo.makedirs('/level2/sublevel2')
        self.assertTrue(self.piwigo.removedirs('/level2'))
        self.assertFalse(self.piwigo.iscategory('/level2'))
        self.piwigo.logout()

    def test_uploadImage(self):
        self.piwigo.login(self.usertest, self.passwordtest)
        self.piwigo.mkdir('/level')
        img = os.path.join(os.path.dirname(os.path.abspath(__file__)),'samplepiwigotools.jpg')
        id = self.piwigo.upload(image=img, path="/level")
        self.assertTrue(id)
        self.assertTrue(self.piwigo.isimage('/level/samplepiwigotools.jpg'))
        self.piwigo.pwg.images.delete(image_id=id, pwg_token=self.piwigo.token)
        self.piwigo.removedirs('/level')
        self.piwigo.logout()

    def test_removeImage(self):
        self.piwigo.login(self.usertest, self.passwordtest)
        self.piwigo.mkdir('/level')
        img = os.path.join(os.path.dirname(os.path.abspath(__file__)),'samplepiwigotools.jpg')
        id = self.piwigo.upload(image=img, path="/level")
        self.assertTrue(self.piwigo.remove('/level/samplepiwigotools.jpg'))
        self.assertFalse(self.piwigo.isimage('/level/samplepiwigotools.jpg'))
        self.piwigo.removedirs('/level')
        self.piwigo.logout()

    def test_sublevel(self):
        self.piwigo.login(self.usertest, self.passwordtest)
        self.piwigo.makedirs('/level2/sublevel2')
        self.assertTrue(len(self.piwigo.sublevels('/level2')))
        self.piwigo.removedirs('/level2')
        self.piwigo.logout()

    def test_downloadImage(self):
        self.piwigo.login(self.usertest, self.passwordtest)
        self.piwigo.mkdir('/level')
        img = os.path.join(os.path.dirname(os.path.abspath(__file__)),'samplepiwigotools.jpg')
        id = self.piwigo.upload(image=img, path="/level")
        imgdst = os.path.join(os.path.dirname(os.path.abspath(__file__)),'download.jpg')
        self.assertTrue(self.piwigo.download("/level/samplepiwigotools.jpg",imgdst))
        os.remove(imgdst)
        self.piwigo.remove('/level/samplepiwigotools.jpg')
        self.piwigo.removedirs('/level')
        self.piwigo.logout()

if __name__ == '__main__':
    unittest.main()
