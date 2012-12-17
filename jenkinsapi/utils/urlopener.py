import urllib2
import base64
import kerberos as krb
from urlparse import urlparse

import logging

log = logging.getLogger( __name__ )

class PreemptiveBasicAuthHandler(urllib2.BaseHandler):
    """
    A BasicAuthHandler class that will add Basic Auth headers to a request
    even when there is no basic auth challenge from the server
    Jenkins does not challenge basic auth but expects it to be present
    """
    def __init__(self, password_mgr=None):
        if password_mgr is None:
            password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        self.passwd = password_mgr
        self.add_password = self.passwd.add_password

    def http_request(self,req):
        uri = req.get_full_url()
        user, pw = self.passwd.find_user_password(None,uri)
        log.debug('ADDING REQUEST HEADER for uri (%s): %s:%s' % (uri,user,pw))
        if pw is None: return req
        raw = "%s:%s" % (user, pw)
        auth = 'Basic %s' % base64.b64encode(raw).strip()
        req.add_unredirected_header('Authorization', auth)
        return req

    def https_request(self,req):
        return self.http_request(req)

class KerberosAuthHandler(urllib2.BaseHandler):
    """
    A BaseHandler class that will add Kerberos Auth headers to a request
    """
    def __init__(self,tgt):
        self.tgt = tgt

    def http_request(self,req):
        req.add_unredirected_header('Authorization', 'Negotiate %s' % self.tgt)
        return req

    def https_request(self,req):
        return self.http_request(req)


def mkurlopener( jenkinsuser, jenkinspass, jenkinsurl, proxyhost, proxyport, proxyuser, proxypass ):
    """
     Creates an url opener that works with both jenkins auth and proxy auth
     If no values are provided for the jenkins or proxy vars, a regular opener is returned
    :param jenkinsuser: username for jenkins, str
    :param jenkinspass: password for jenkins, str
    :param jenkinsurl: jenkins url, str
    :param proxyhost: proxy hostname, str
    :param proxyport: proxy port, int
    :param proxyuser: proxy username, str
    :param proxypass: proxy password, str
    :return: urllib2.opener configured for auth
    """
    handlers = []
    for handler in get_jenkins_auth_handler(jenkinsuser=jenkinsuser, jenkinspass=jenkinspass, jenkinsurl=jenkinsurl):
        handlers.append(handler)
    for handler in get_proxy_handler(proxyhost, proxyport, proxyuser, proxypass):
        handlers.append(handler)
    opener = urllib2.build_opener(*handlers)
    return opener.open

def mkkrbopener( jenkinsurl ):
    """
     Creates an url opener that works with kerberos auth

    :param jenkinsurl: jenkins url, str
    :return: urllib2.opener configured for kerberos auth
    """
    handlers = []
    for handler in get_kerberos_auth_handler(jenkinsurl=jenkinsurl):
        handlers.append(handler)
    opener = urllib2.build_opener(*handlers)
    return opener.open


def mkopener(*handlers):
    opener = urllib2.build_opener(*handlers)
    return opener.open

def get_jenkins_auth_handler(jenkinsuser, jenkinspass, jenkinsurl):
    """
    Get a basic authentification handler for jenkins
    :param jenkinsuser: jenkins username, str
    :param jenkinspass: jenkins password, str
    :param jenkinsurl: jenkins base url, str
    :return: a list of handlers
    """
    for param in jenkinsuser, jenkinspass, jenkinsurl:
        if param is None:
            return []
    assert type(jenkinsuser) == str, "Jenkins username should be a string, got %s" % repr(jenkinsuser)
    assert type(jenkinspass) == str, "Jenkins password should be a string, git %s" % repr(jenkinspass)
#    hostname = urlparse.urlsplit(jenkinsurl).hostname
    handler = PreemptiveBasicAuthHandler()
    handler.add_password(None, jenkinsurl, jenkinsuser, jenkinspass)
    log.debug('Adding BasicAuthHandler: url:%s, user:%s,' % (jenkinsurl, jenkinsuser))
    return [ handler ]

def get_proxy_handler(proxyhost, proxyport, proxyuser, proxypass):
    """
    Get a configured handler for a proxy

    :param proxyhost: proxy hostname, str
    :param proxyport: proxy port, int
    :param proxyuser: proxy username, str
    :param proxypass: proxy password, str
    :return: list of handlers
    """
    for param in proxyhost, proxyport, proxyuser, proxypass:
        if param is None:
            return []
    assert type( proxyport ) == int, "Proxy port should be an int, got %s" % repr( proxyport )
    assert type( proxypass ) == str, "Proxy password should be a sting, got %s" % repr( proxypass )
    assert type( proxyuser ) == str, "Proxy username should be a string, got %s" % repr( proxyuser )

    proxy_spec = { 'http': 'http://%s:%i/' % (proxyhost, proxyport),
                   'https': 'http://%s:%i/' % (proxyhost, proxyport) }

    proxy_handler = urllib2.ProxyHandler( proxy_spec )
    proxy_auth_handler = urllib2.HTTPBasicAuthHandler()
    proxy_auth_handler.add_password( None, proxyhost, proxyuser, proxypass )
    return [proxy_handler, proxy_auth_handler]


def get_kerberos_auth_handler(jenkinsurl):
    """
    Get a handler which enabled authentication over GSSAPI

    :param jenkinsurl: jenkins base url, str
    :return: a list of handlers
    """
    jenkinsnetloc = urlparse(jenkinsurl).netloc
    assert type( jenkinsnetloc ) == str, "Jenkins network location should be a string, got %s" % repr( jenkinsnetloc )

    _ignore, ctx = krb.authGSSClientInit('HTTP@%s' % jenkinsnetloc, gssflags=krb.GSS_C_DELEG_FLAG|krb.GSS_C_MUTUAL_FLAG|krb.GSS_C_SEQUENCE_FLAG)
    rc = krb.authGSSClientStep(ctx,'')
    if rc != krb.AUTH_GSS_CONTINUE:
        return []
    tgt = krb.authGSSClientResponse(ctx)
    if not tgt:
        return []

    krb_handler = KerberosAuthHandler(tgt)
    return [ krb_handler ]

class NoAuto302Handler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, hdrs):
        return fp

