#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2016 Hive Solutions Lda.
#
# This file is part of Hive Appier Framework.
#
# Hive Appier Framework is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Appier Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Appier Framework. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2016 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import json
import base64
import string
import random
import logging
import threading

from . import util
from . import common
from . import legacy
from . import typesf
from . import config
from . import exceptions

TIMEOUT = 60
""" The timeout in seconds to be used for the blocking
operations in the http connection, this value avoid unwanted
blocking operations to remain open for an infinite time """

RANGE = string.ascii_letters + string.digits
""" The range of characters that are going to be used in
the generation of the boundary value for the mime """

SEQUENCE_TYPES = (list, tuple)
""" The sequence defining the various types that are
considered to be sequence based for python """

AUTH_ERRORS = (401, 403, 440, 499)
""" The sequence that defines the various http errors
considered to be authentication related and for which a
new authentication try will be performed """

ACCESS_LOCK = threading.RLock()
""" Global access lock used for locking global operations
that required thread safety under the http infra-structure """

def try_auth(auth_callback, params, headers = None):
    if not auth_callback: raise
    if headers == None: headers = dict()
    auth_callback(params, headers)

def get_f(*args, **kwargs):
    name = kwargs.pop("name", "default")
    kwargs["handle"] = kwargs.get("handle", True)
    kwargs["redirect"] = kwargs.get("redirect", True)
    data, response = get(*args, **kwargs)
    info = response.info()
    mime = info.get("Content-Type", None)
    file_tuple = util.FileTuple((name, mime, data))
    return typesf.File(file_tuple)

def get(
    url,
    params = None,
    headers = None,
    handle = None,
    redirect = None,
    auth_callback = None
):
    return _method(
        _get,
        url,
        params = params,
        headers = headers,
        handle = handle,
        redirect = redirect,
        auth_callback = auth_callback
    )

def post(
    url,
    params = None,
    data = None,
    data_j = None,
    data_m = None,
    headers = None,
    mime = None,
    handle = None,
    redirect = None,
    auth_callback = None
):
    return _method(
        _post,
        url,
        params = params,
        data = data,
        data_j = data_j,
        data_m = data_m,
        headers = headers,
        mime = mime,
        handle = handle,
        redirect = redirect,
        auth_callback = auth_callback
    )

def put(
    url,
    params = None,
    data = None,
    data_j = None,
    data_m = None,
    headers = None,
    mime = None,
    handle = None,
    redirect = None,
    auth_callback = None
):
    return _method(
        _put,
        url,
        params = params,
        data = data,
        data_j = data_j,
        data_m = data_m,
        headers = headers,
        mime = mime,
        handle = handle,
        redirect = redirect,
        auth_callback = auth_callback
    )

def delete(
    url,
    params = None,
    headers = None,
    handle = None,
    redirect = None,
    auth_callback = None
):
    return _method(
        _delete,
        url,
        params = params,
        headers = headers,
        handle = handle,
        redirect = redirect,
        auth_callback = auth_callback
    )

def patch(
    url,
    params = None,
    data = None,
    data_j = None,
    data_m = None,
    headers = None,
    mime = None,
    handle = None,
    redirect = None,
    auth_callback = None
):
    return _method(
        _patch,
        url,
        params = params,
        data = data,
        data_j = data_j,
        data_m = data_m,
        headers = headers,
        mime = mime,
        handle = handle,
        redirect = redirect,
        auth_callback = auth_callback
    )

def _method(method, *args, **kwargs):
    try:
        auth_callback = kwargs.pop("auth_callback", None)
        result = method(*args, **kwargs)
    except legacy.HTTPError as error:
        try:
            params = kwargs.get("params", None)
            headers = kwargs.get("headers", None)
            if not error.code in AUTH_ERRORS : raise
            try_auth(auth_callback, params, headers)
            result = method(*args, **kwargs)
        except legacy.HTTPError as error:
            code = error.getcode()
            raise exceptions.HTTPError(error, code)

    return result

def _get(
    url,
    params = None,
    headers = None,
    handle = None,
    redirect = None
):
    return _method_empty(
        "GET",
        url,
        params = params,
        headers = headers,
        handle = handle,
        redirect = redirect
    )

def _post(
    url,
    params = None,
    data = None,
    data_j = None,
    data_m = None,
    headers = None,
    mime = None,
    handle = None,
    redirect = None
):
    return _method_payload(
        "POST",
        url,
        params = params,
        data = data,
        data_j = data_j,
        data_m = data_m,
        headers = headers,
        mime = mime,
        handle = handle,
        redirect = redirect
    )

def _put(
    url,
    params = None,
    data = None,
    data_j = None,
    data_m = None,
    headers = None,
    mime = None,
    handle = None,
    redirect = None
):
    return _method_payload(
        "PUT",
        url,
        params = params,
        data = data,
        data_j = data_j,
        data_m = data_m,
        headers = headers,
        mime = mime,
        handle = handle,
        redirect = redirect
    )

def _delete(
    url,
    params = None,
    headers = None,
    handle = None,
    redirect = None
):
    return _method_empty(
        "DELETE",
        url,
        params = params,
        headers = headers,
        handle = handle,
        redirect = redirect
    )

def _patch(
    url,
    params = None,
    data = None,
    data_j = None,
    data_m = None,
    headers = None,
    mime = None,
    handle = None,
    redirect = None
):
    return _method_payload(
        "PATCH",
        url,
        params = params,
        data = data,
        data_j = data_j,
        data_m = data_m,
        headers = headers,
        mime = mime,
        handle = handle,
        redirect = redirect
    )

def _method_empty(
    name,
    url,
    params = None,
    headers = None,
    handle = None,
    redirect = None,
    timeout = TIMEOUT
):
    if handle == None: handle = False
    if redirect == None: redirect = False
    values = params or dict()

    logging.info("%s %s with '%s'" % (name, url, str(values)))

    url, scheme, host, authorization, extra = _parse_url(url)
    if extra: values.update(extra)
    data = _urlencode(values)

    headers = headers or dict()
    if host: headers["Host"] = host
    if authorization: headers["Authorization"] = "Basic %s" % authorization
    url = url + "?" + data if data else url
    url = str(url)

    file = _resolve(url, name, headers, None, timeout)
    try: result = file.read()
    finally: file.close()

    code = file.getcode()
    info = file.info()

    location = info.get("Location", None) if redirect else None
    if location: return _redirect(location, scheme, host, handle, redirect)

    logging.info("%s %s returned '%d'" % (name, url, code))

    result = _result(result, info)
    return (result, file) if handle else result

def _method_payload(
    name,
    url,
    params = None,
    data = None,
    data_j = None,
    data_m = None,
    headers = None,
    mime = None,
    handle = None,
    redirect = None,
    timeout = TIMEOUT
):
    if handle == None: handle = False
    if redirect == None: redirect = False
    values = params or dict()

    logging.info("%s %s with '%s'" % (name, url, str(params)))

    url, scheme, host, authorization, extra = _parse_url(url)
    if extra: values.update(extra)
    data_e = _urlencode(values)

    if not data == None:
        url = url + "?" + data_e if data_e else url
    elif not data_j == None:
        data = json.dumps(data_j)
        url = url + "?" + data_e if data_e else url
        mime = mime or "application/json"
    elif not data_m == None:
        url = url + "?" + data_e if data_e else url
        content_type, data = _encode_multipart(
            data_m, mime = mime, doseq = True
        )
        mime = content_type
    elif data_e:
        data = data_e
        mime = mime or "application/x-www-form-urlencoded"

    data = legacy.bytes(data)
    length = len(data) if data else 0

    headers = headers or dict()
    headers["Content-Length"] = length
    if mime: headers["Content-Type"] = mime
    if host: headers["Host"] = host
    if authorization: headers["Authorization"] = "Basic %s" % authorization
    url = str(url)

    file = _resolve(url, name, headers, data, timeout)
    try: result = file.read()
    finally: file.close()

    code = file.getcode()
    info = file.info()

    location = info.get("Location", None) if redirect else None
    if location: return _redirect(location, scheme, host, handle, redirect)

    logging.info("%s %s returned '%d'" % (name, url, code))

    result = _result(result, info)
    return (result, file) if handle else result

def _redirect(location, scheme, host, handle, redirect):
    is_relative = location.startswith("/")
    if is_relative: location = scheme + "://" + host + location
    return get(
        location,
        handle = handle,
        redirect = redirect
    )

def _resolve(*args, **kwargs):
    _global = globals()
    client = config.conf("HTTP_CLIENT", "netius")
    client = kwargs.pop("client", client)
    resolver = _global.get("_resolve_" + client, _resolve_legacy)
    try: result = resolver(*args, **kwargs)
    except ImportError: result = _resolve_legacy(*args, **kwargs)
    return result

def _resolve_legacy(url, method, headers, data, timeout, **kwargs):
    opener = legacy.build_opener(legacy.HTTPHandler)
    request = legacy.Request(url, data = data, headers = headers)
    request.get_method = lambda: method
    return opener.open(request, timeout = timeout)

def _resolve_netius(url, method, headers, data, timeout, **kwargs):
    import netius.clients

    # converts the provided dictionary of headers into a new map to
    # allow any re-writing of values, valuable for a re-connect
    headers = dict(headers)

    # retrieves the various dynamic parameters for the http client
    # usage under the netius infra-structure
    retry = kwargs.get("retry", 1)
    reuse = kwargs.get("reuse", True)

    # verifies if client re-usage must be enforced and if that's the
    # case the global client object is requested (singleton) otherwise
    # the client should be created inside the http client static method
    http_client = _client_netius() if reuse else None
    result = netius.clients.HTTPClient.method_s(
        method,
        url,
        headers = headers,
        data = data,
        async = False,
        http_client = http_client
    )

    # tries to retrieve any possible error coming from the result object
    # if this happens it means an exception has been raised internally and
    # the error should be handled in a proper manner, if the error is related
    # to a closed connection a retry may be performed to try to re-establish
    # the connection (allows for reconnection in connection pool)
    error = result.get("error", None)
    if error == "closed":
        if retry < 1: raise exceptions.OperationalError(message = "Connection closed")
        kwargs["retry"] = retry - 1
        return _resolve_netius(
            url, method, headers, data, timeout, **kwargs
        )

    # converts the netius specific result map into a response compatible
    # object (equivalent to the urllib one) to be used by the upper layers
    # under an equivalent and compatible approach
    response = netius.clients.HTTPClient.to_response(result)

    # retrieves the response code of the created response and verifies if
    # it represent an error, if that's the case raised an error exception
    # to the upper layers to break the current execution logic properly
    code = response.getcode()
    is_error = code // 100 in (4, 5) if code else True
    if is_error: raise legacy.HTTPError(
        url, code, "HTTP retrieval problem", None, response
    )

    # returns the final response object to the upper layers, this object
    # may be used freely under the compatibility interface it provides
    return response

def _client_netius():
    import netius.clients
    global _netius_clients

    # retrieves the reference to the current thread and uses the value
    # to retrieve the thread identifier (tid) for it, to be used in the
    # identification of the client resource associated with it
    tid = threading.current_thread().ident

    # acquires the global http lock and executes a series of validation
    # and initialization of the netius client infra-structure, this
    # operations required thread safety
    ACCESS_LOCK.acquire()
    try:
        registered = "_netius_clients" in globals()
        _netius_clients = _netius_clients if registered else dict()
        netius_client = _netius_clients.get(tid, None)
    finally:
        ACCESS_LOCK.release()

    # in case a previously created netius client has been retrieved
    # returns it to the caller method for proper re-usage
    if netius_client: return netius_client

    # creates the "new" http client for the current thread and registers
    # it under the netius client structure so that it may be re-used
    netius_client = netius.clients.HTTPClient(
        thread = False,
        auto_pause = True
    )
    _netius_clients[tid] = netius_client

    # in case this is the first registration of the dictionary a new on
    # exit callback is registered to cleanup the netius infra-structure
    # then the final client is returned to the caller of the method
    if not registered: common.base().on_exit(_cleanup_netius)
    return netius_client

def _cleanup_netius():
    global _netius_clients
    for netius_client in _netius_clients.values(): netius_client.cleanup()
    del _netius_clients

def _parse_url(url):
    parse = legacy.urlparse(url)
    scheme = parse.scheme
    secure = scheme == "https"
    default = 443 if secure else 80
    port = parse.port or default
    url = parse.scheme + "://" + parse.hostname + ":" + str(port) + parse.path
    if port in (80, 443): host = parse.hostname
    else: host = parse.hostname + ":" + str(port)
    username = parse.username
    password = parse.password
    authorization = _authorization(username, password)
    params = _params(parse.query)
    return (url, scheme, host, authorization, params)

def _result(data, info = {}, force = False, strict = False):
    # tries to retrieve the content type value from the headers
    # info and verifies if the current data is json encoded, so
    # that it gets automatically decoded for such cases
    content_type = info.get("Content-Type", None) or ""
    is_json = content_type.startswith((
        "application/json",
        "text/json",
        "text/javascript"
    )) or force

    # verifies if the current result set is json encoded and in
    # case it's decodes it and loads it as json otherwise returns
    # the "raw" data to the caller method as expected, note that
    # the strict flag is used to determine if the exception should
    # be re-raised to the upper level in case of value error
    if is_json and legacy.is_bytes(data): data = data.decode("utf-8")
    try: data = json.loads(data) if is_json else data
    except ValueError:
        if strict: raise
    return data

def _params(query):
    # creates the dictionary that is going to be used to store the
    # complete information regarding the parameters in query
    params = dict()

    # validates that the provided query value is valid and if
    # that's not the case returns the created parameters immediately
    # (empty parameters are returned)
    if not query: return params

    # splits the query value around the initial parameter separator
    # symbol and iterates over each of them to parse them and create
    # the proper parameters dictionary (of lists)
    query_s = query.split("&")
    for part in query_s:
        parts = part.split("=", 1)
        if len(parts) == 1: value = ""
        else: value = parts[1]
        key = parts[0]
        key = legacy.unquote_plus(key)
        value = legacy.unquote_plus(value)
        param = params.get(key, [])
        param.append(value)
        params[key] = param

    # returns the final parameters dictionary to the caller method
    # so that it may be used as a proper structure representation
    return params

def _urlencode(values, as_string = True):
    # creates the dictionary that will hold the final
    # dictionary of values (without the unset and
    # invalid values)
    final = dict()

    # iterates over all the items in the values map to
    # try to filter the values that are not valid
    for key, value in values.items():
        # creates the list that will hold the valid values
        # of the current key in iteration (sanitized values)
        _values = []

        # in case the current data type of the key is unicode
        # the value must be converted into a string using the
        # default utf encoding strategy (as defined)
        if type(key) == legacy.UNICODE: key = key.encode("utf-8")

        # verifies the type of the current value and in case
        # it's sequence based converts it into a list using
        # the conversion method otherwise creates a new list
        # and includes the value in it
        value_t = type(value)
        if value_t in SEQUENCE_TYPES: value = list(value)
        else: value = [value]

        # iterates over all the values in the current sequence
        # and adds the valid values to the sanitized sequence,
        # this includes the conversion from unicode string into
        # a simple string using the default utf encoder
        for _value in value:
            if _value == None: continue
            is_string = type(_value) in legacy.STRINGS
            if not is_string: _value = str(_value)
            is_unicode = type(_value) == legacy.UNICODE
            if is_unicode: _value = _value.encode("utf-8")
            _values.append(_value)

        # sets the sanitized list of values as the new value for
        # the key in the final dictionary of values
        final[key] = _values

    # in case the "as string" flag is not set the ended key to value
    # dictionary should be returned to the called method and not the
    # "default" linear and string based value
    if not as_string: return final

    # runs the encoding with sequence support on the final map
    # of sanitized values and returns the encoded result to the
    # caller method as the encoded value
    return legacy.urlencode(final, doseq = True)

def _quote(values, plus = False, safe = "/"):
    method = legacy.quote_plus if plus else legacy.quote
    values = _urlencode(values, as_string = False)

    final = dict()

    for key, value in values.items():
        key = method(key, safe = safe)
        value = method(value[0], safe = safe)
        final[key] = value

    return final

def _authorization(username, password):
    if not username: return None
    if not password: return None
    payload = "%s:%s" % (username, password)
    payload = legacy.bytes(payload)
    authorization = base64.b64encode(payload)
    authorization = legacy.str(authorization)
    return authorization

def _encode_multipart(fields, mime = None, doseq = False):
    mime = mime or "multipart/form-data"
    boundary = _create_boundary(fields, doseq = doseq)
    boundary_b = legacy.bytes(boundary)

    buffer = []

    for key, values in fields.items():
        is_list = doseq and type(values) == list
        values = values if is_list else [values]

        for value in values:

            if isinstance(value, dict):
                header_l = []
                data = None
                for key, item in value.items():
                    if key == "data": data = item
                    else: header_l.append("%s: %s" % (key, item))
                value = data
                header = "\r\n".join(header_l)
            elif isinstance(value, tuple):
                content_type = None
                if len(value) == 2: name, contents = value
                else: name, content_type, contents = value
                header = "Content-Disposition: form-data; name=\"%s\"; filename=\"%s\"" %\
                    (key, name)
                if content_type: header += "\r\nContent-Type: %s" % content_type
                value = contents
            else:
                header = "Content-Disposition: form-data; name=\"%s\"" % key
                value = _encode(value)

            header = _encode(header)
            value = _encode(value)

            buffer.append(b"--" + boundary_b)
            buffer.append(header)
            buffer.append(b"")
            buffer.append(value)

    buffer.append(b"--" + boundary_b + b"--")
    buffer.append(b"")
    body = b"\r\n".join(buffer)
    content_type = "%s; boundary=%s" % (mime, boundary)

    return content_type, body

def _create_boundary(fields, size = 32, doseq = False):
    while True:
        base = "".join(random.choice(RANGE) for _value in range(size))
        boundary = "----------" + base
        result = _try_boundary(fields, boundary, doseq = doseq)
        if result: break

    return boundary

def _try_boundary(fields, boundary, doseq = False):
    boundary_b = legacy.bytes(boundary)

    for key, values in fields.items():
        is_list = doseq and type(values) == list
        values = values if is_list else [values]

        for value in values:
            value_t = type(value)

            if value_t == dict: name = ""; value = value.get("data", b"")
            elif value_t == tuple: name = value[0]; value = value[1]
            else: name = ""; value = _encode(value)

            if not key.find(boundary) == -1: return False
            if not name.find(boundary) == -1: return False
            if not value.find(boundary_b) == -1: return False

    return True

def _encode(value, encoding = "utf-8"):
    value_t = type(value)
    if value_t == legacy.BYTES: return value
    elif value_t == legacy.UNICODE: return value.encode(encoding)
    return legacy.bytes(str(value))
