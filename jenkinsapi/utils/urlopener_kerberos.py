# import urllib2
# import kerberos as krb
# from urlparse import urlparse

# class KerberosAuthHandler(urllib2.BaseHandler):
#     """
#     A BaseHandler class that will add Kerberos Auth headers to a request
#     """
#     def __init__(self,tgt):
#         self.tgt = tgt

#     def http_request(self,req):
#         req.add_unredirected_header('Authorization', 'Negotiate %s' % self.tgt)
#         return req

#     def https_request(self,req):
#         return self.http_request(req)

# def mkkrbopener( jenkinsurl ):
#     """
#      Creates an url opener that works with kerberos auth

#     :param jenkinsurl: jenkins url, str
#     :return: urllib2.opener configured for kerberos auth
#     """
#     handlers = []
#     for handler in get_kerberos_auth_handler(jenkinsurl=jenkinsurl):
#         handlers.append(handler)
#     opener = urllib2.build_opener(*handlers)
#     return opener.open

# def get_kerberos_auth_handler(jenkinsurl):
#     """
#     Get a handler which enabled authentication over GSSAPI

#     :param jenkinsurl: jenkins base url, str
#     :return: a list of handlers
#     """
#     jenkinsnetloc = urlparse(jenkinsurl).netloc
#     assert type( jenkinsnetloc ) == str, "Jenkins network location should be a string, got %s" % repr( jenkinsnetloc )

#     _ignore, ctx = krb.authGSSClientInit('HTTP@%s' % jenkinsnetloc, gssflags=krb.GSS_C_DELEG_FLAG|krb.GSS_C_MUTUAL_FLAG|krb.GSS_C_SEQUENCE_FLAG)
#     rc = krb.authGSSClientStep(ctx,'')
#     if rc != krb.AUTH_GSS_CONTINUE:
#         return []
#     tgt = krb.authGSSClientResponse(ctx)
#     if not tgt:
#         return []

#     krb_handler = KerberosAuthHandler(tgt)
#     return [ krb_handler ]
