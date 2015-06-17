"""
OAuth2 / OpenID Connect authentication related views
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

# @@TODO: refactor all OAuth2 details from views to this module
# @@TODO: define a view decorator to apply OAuth2 authentication requirement

import os
import re
import json
import copy
import uuid
import urllib
from urlparse import urlparse, urljoin
from importlib import import_module

import logging
log = logging.getLogger(__name__)

import httplib2

from oauth2client.client import OAuth2WebServerFlow
from oauth2client import xsrfutil
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from oauth2client.django_orm import Storage

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext, loader
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

settings = import_module(os.environ["DJANGO_SETTINGS_MODULE"])

from utils.http_errors import error400values

from models import CredentialsModel

# Per-instance generated secret key for CSRF protection via OAuth2 state value.
# Regenerated each time this service is started.
FLOW_SECRET_KEY = str(uuid.uuid1())

PROVIDER_LIST = None

CLIENT_SECRETS = None

SCOPE_DEFAULT = "openid profile email"

OAuth2WebServerFlow_strip = (
    "step1_get_authorize_url",
    "step2_exchange"
    )

def collect_client_secrets():
    global CLIENT_SECRETS, PROVIDER_LIST
    if CLIENT_SECRETS is None:
        CLIENT_SECRETS = {}
        PROVIDER_LIST  = {}
        clientsecrets_dirname = os.path.join(settings.CONFIG_BASE, "providers/")
        if os.path.isdir(clientsecrets_dirname):
            clientsecrets_files   = os.listdir(clientsecrets_dirname)
            for f in clientsecrets_files:
                p = os.path.join(clientsecrets_dirname,f)
                j = json.load(open(p, "r"))
                n = j['web']['provider']
                CLIENT_SECRETS[n] = j['web']
                PROVIDER_LIST[n]  = p
    return

def object_to_dict(obj, strip):
    """Utility function that creates dictionary representation of an object.

    Args:
        strip: an array of names of members to not include in the dict.

    Returns:
        dictionary, with non-excluded values that can be used to reconstruct an instance
        of the object via its constructor (assuming an appropriate constructor form, as
        used below for dict_to_flow)
    """
    t = type(obj)
    d = copy.copy(obj.__dict__)
    for member in strip:
      if member in d:
        del d[member]
    d['_class'] = t.__name__
    d['_module'] = t.__module__
    return d

def flow_to_dict(f):
    return object_to_dict(f, OAuth2WebServerFlow_strip) 

def dict_to_flow(d):
    """
    Constructs a OAuth2WebServerFlow object from a dictionary previously created
    by flow_to_dict.

    Args:
        d:  dict, generated by object_to_dict
    """
    flow = OAuth2WebServerFlow(
        d['client_id'], d['client_secret'], d['scope'],
        redirect_uri=d['redirect_uri'], 
        user_agent=d['user_agent'],
        auth_uri=d['auth_uri'], 
        token_uri=d['token_uri'],
        revoke_uri=d['revoke_uri'],
        **d['params']
        )
    return flow

def authentication_required(
        login_form_uri=None, login_post_uri=None, login_done_uri=None, 
        continuation_url=None, scope=SCOPE_DEFAULT):
    """
    Decorator for view handler function that activates OAuth2 authentication flow
    if the current request is not already associated with an authenticated user.
    """
    # @@NOTE: not tested; the mix of static and dynamic parameters required makes
    #         the in-line form easier to use than a decorator.
    def decorator(func):
        def guard(view, values):
            return (
                confirm_authentication(view, 
                    login_form_uri, login_post_uri, login_done_uri, 
                    continuation_url, scope)
            or
                func(view, values)
            )
        return guard
    return decorator

def HttpResponseRedirectWithQuery(redirect_uri, query_params):
    nq = "?"
    for pname in query_params.keys():
        redirect_uri += nq + pname + "=" + urllib.quote(query_params[pname])
        nq = "&"
    # log.info("redirect_uri: "+redirect_uri)
    return HttpResponseRedirect(redirect_uri)

def HttpResponseRedirectLoginWithMessage(request, message):
    login_form_uri = request.session['login_form_uri']
    log.info("login_form_uri: "+login_form_uri)
    query_params = (
        { "continuation": request.session['continuation_url']
        , "scope":        request.session['oauth2_scope']
        , "message":      message
        })
    return HttpResponseRedirectWithQuery(login_form_uri, query_params)

# Authentication and authorization
def confirm_authentication(view, 
        login_form_uri=None, login_post_uri=None, login_done_uri=None, 
        continuation_url=None, scope=SCOPE_DEFAULT):
    """
    Return None if required authentication is present, otherwise
    a login redirection response to the supplied URI

    view.credential is set to credential that can be used to access resource
    """
    if view.request.user.is_authenticated():
        storage         = Storage(CredentialsModel, 'id', view.request.user, 'credential')
        view.credential = storage.get()
        # log.info("view.credential %r"%(view.credential,))
        if view.credential is not None:
            if not view.credential.invalid:
                return None         # Valid credential present: proceed...
        else:
            # Django login with local credential: check for user email address
            #
            # @@TODO: is this safe?
            # 
            # NOTE: currently, view.credential is provided by the oauth2 and used
            # only for the .invalid test above.  If it is ever used by other 
            # application components, it may be necessary to construct a
            # credential for local logins.  In the long run, if credentials will
            # be used to access third party services or resources, it may not be 
            # possible to use non-Oauth2 credentials here.  In the meanwhile,
            # allowing local Django user credentials provides an easier route for
            # getting a software instance installed for evaluation purposes.
            #
            if view.request.user.email:
                return None        # Assume valid login: proceed...
            else:
                return error400values(view, "Local user has no email address")
    if not login_form_uri:
        return error400values(view, "No login form URI specified")
    if not login_done_uri:
        return error400values(view, "No login completion URI specified")
    if not login_post_uri:
        login_post_uri = login_form_uri
    if not continuation_url:
        continuation_url = view.request.path
    # Redirect to initiate login sequence 
    view.request.session['login_form_uri']   = login_form_uri
    view.request.session['login_post_uri']   = login_post_uri
    view.request.session['login_done_uri']   = login_done_uri
    view.request.session['continuation_url'] = continuation_url
    view.request.session['oauth2_scope']     = scope
    query_params = (
        { "continuation": continuation_url
        , "scope":        scope
        , "message":      ""
        })
    return HttpResponseRedirectWithQuery(login_form_uri, query_params)

class LoginUserView(generic.View):
    """
    View class to present login form to gather user id and other login information.

    The login page solicits a user id and an identity provider

    The login page supports the following request parameters:

    continuation={uri}
    - a URI that is retrieved, with a suitable authorization grant as a parameter, 
      when appropriate permission has been confirmed by an authenticated user.
    scope={string}
    - requested or required access scope
    """

    def get(self, request):
        collect_client_secrets()
        # @@TODO: check PROVIDER_LIST, report error if none here
        # Retrieve request parameters
        continuation = request.GET.get("continuation", "/no-login-continuation/")
        scope        = request.GET.get("scope",        SCOPE_DEFAULT)
        message      = request.GET.get("message",      "")
        # Check required values in session - if missing, restart sequence from original URI
        # This is intended to avoid problems if this view is invoked out of sequence
        login_post_uri = request.session.get('login_post_uri', None)
        login_done_uri = request.session.get('login_done_uri', None)
        if (login_post_uri is None) or (login_done_uri is None):
            return HttpResponseRedirect(continuation)
        # Display login form
        default_provider = ""
        if len(PROVIDER_LIST.keys()) > 0:
            default_provider = PROVIDER_LIST.keys()[0]
        logindata = (
            { "login_post":     request.session['login_post_uri']
            , "login_done":     request.session['login_done_uri']
            , "continuation":   continuation
            , "userid":         request.GET.get("userid", "")
            , "providers":      PROVIDER_LIST.keys()
            , "scope":          scope
            , "message":        message
            , "suppress_user":  True
            # Default provider
            , "provider":       default_provider
            , 'help_filename':  'login-help'
            })
        # Load help text if available
        # @@NOTE: this next is dependent on data provided by the calling app?
        if 'help_filename' in logindata:
            help_filepath = os.path.join(
                settings.SITE_SRC_ROOT, 
                "annalist/views/help/%s.html"%logindata['help_filename']
                )
            if os.path.isfile(help_filepath):
                with open(help_filepath, "r") as helpfile:
                    logindata['help_text'] = helpfile.read()
        # Render form & return control to browser
        template = loader.get_template('login.html')
        context  = RequestContext(self.request, logindata)
        return HttpResponse(template.render(context))

class LoginPostView(generic.View):
    """
    View class initiate an OAuth2 authorization (or similar) flow, typically on POST
    of a login form.

    It saves the supplied user id in a session value, and redirects the user to the 
    identity provider, which in due course returns control to the application along 
    with a suitable authorization grant.

    The login form provides the following values:

    userid={string}
    - a user identifying string that will be associated with the external service
      login credentials.
    provider={string}
    - a string that identifiues a provioder selectred to proviode authentication/
      authorization for the indicated user.  This string is an index to PROVIDER_LIST,
      which in turn contains filenames for client secrets to user when using the 
      indicated identity provider.
    login_done={uri}
    - a URI that is retrieved, with a suitable authorization grant as a parameter, 
      when appropriate permission has been confirmed by an authenticated user.
      Communicated via a hidden form value.
    continuation={uri}
    - a URI that is retrieved, with a suitable authorization grant as a parameter, 
      when appropriate permission has been confirmed by an authenticated user.
      Communicated via a hidden form value.
    scope={string}
    - Requested or required access scope, communicated via a hidden form value.
    """

    def post(self, request):
        # Retrieve request parameters
        userid        = request.POST.get("userid",        "")
        provider      = request.POST.get("provider",      "Google")
        login_done    = request.POST.get("login_done",    "/no_login_done_in_form_response/")
        continuation  = request.POST.get("continuation",  "/no_continuation_in_form_response/")
        scope         = request.POST.get("scope",         SCOPE_DEFAULT) 
        # Access or create flow object for this session
        if request.POST.get("login", None) == "Login":
            collect_client_secrets()
            # Create and initialize flow object
            clientsecrets_filename = os.path.join(
                settings.CONFIG_BASE, "providers/", PROVIDER_LIST[provider]
                )
            flow = flow_from_clientsecrets(
                clientsecrets_filename,
                scope=scope,
                redirect_uri=request.build_absolute_uri(login_done)
                )
            flow.params['state']        = xsrfutil.generate_token(FLOW_SECRET_KEY, request.user)
            flow.params['provider']     = provider
            flow.params['userid']       = userid
            # flow.params['scope']        = scope
            flow.params['continuation'] = continuation
            # Save flow object in Django session
            request.session['oauth2flow'] = flow_to_dict(flow)
            # Initiate OAuth2 dance
            auth_uri = flow.step1_get_authorize_url()
            return HttpResponseRedirect(auth_uri)
        # Login cancelled: redirect to continuation
        # (which may just redisplay the login page)
        return HttpResponseRedirect(continuation)

class LoginDoneView(generic.View):
    """
    View class used to complete login process with authorization grant provided by
    authorization server.
    """

    def get(self, request):
        # Look for authorization grant
        flow   = dict_to_flow(request.session['oauth2flow'])
        userid = flow.params['userid']
        if not userid:
            log.info("No User ID specified")
            return HttpResponseRedirectLoginWithMessage(request, "No User ID specified")
        if not re.match(r"\w+$", userid):
            return HttpResponseRedirectLoginWithMessage(request, 
                "User ID must consist of letters, digits and '_' chacacters (%s)"%(userid))
        # Save copy of current user details, if defined
        try:
            olduser = User.objects.get(username=userid)
        except User.DoesNotExist:
            olduser = None
        # Get authenticated user details
        try:
            credential = flow.step2_exchange(request.REQUEST) # Raises FlowExchangeError if a problem occurs
            authuser = authenticate(
                username=userid, password=credential, 
                profile_uri=CLIENT_SECRETS[flow.params['provider']]['profile_uri']
                )
        except FlowExchangeError, e:
            log.error("CLIENT_SECRETS %r"%(CLIENT_SECRETS[flow.params['provider']],))
            return HttpResponseRedirectLoginWithMessage(request, str(e))
        # Check authenticated details for user id match any previous values.
        #
        # The user id is entered by the user on the login form, and is used as a key to
        # access authenticated user details in the Django user database.  The user id 
        # itself is not checked by the Oauth2 login flow, other than for checking that
        # it containbs only work characters
        #
        # Instead, we trust that the associated email address has been confirmed by the 
        # OAuth2 provider, and don't allow login where the email adress differs from any 
        # currently saved email address for the user id used..  This aims to  prevent a 
        # new set of OAuth2 credentials being used for a previously created Django user id.
        #
        if not authuser.email:
            return HttpResponseRedirectLoginWithMessage(request, 
                "No email address associated with authenticated user %s"%(userid))
        if olduser:
            if authuser.email != olduser.email:
                return HttpResponseRedirectLoginWithMessage(request, 
                    "Authenticated user %s email address mismatch (%s, %s)"%
                        (userid, authuser.email, olduser.email))
        # Complete the login and save details
        authuser.save()
        login(request, authuser)
        storage    = Storage(CredentialsModel, 'id', request.user, 'credential')
        storage.put(credential)
        # Don't normally log the credential/token as they might represent a security leakage:
        # log.debug("LoginDoneView: credential:      "+repr(credential.to_json()))
        # log.info("LoginDoneView: id_token:        "+repr(credential.id_token))
        log.info("LoginDoneView: user.username:   "+authuser.username)
        log.info("LoginDoneView: user.first_name: "+authuser.first_name)
        log.info("LoginDoneView: user.last_name:  "+authuser.last_name)
        log.info("LoginDoneView: user.email:      "+authuser.email)
        return HttpResponseRedirect(flow.params['continuation'])

class LogoutUserView(generic.View):
    """
    View class to handle logout
    """

    def get(self, request):
        logout(request)
        continuation = request.GET.get("continuation", urljoin(urlparse(request.path).path, "../"))
        return HttpResponseRedirect(continuation)

# End.
