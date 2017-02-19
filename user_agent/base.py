# -*- coding: utf-8 -*-
# pylint: disable=line-too-long
"""
This module is for generating random, valid web navigator's
    configs & User-Agent HTTP headers.

Functions:
* generate_user_agent: generates User-Agent HTTP header
* generate_navigator:  generates web navigator's config

FIXME:
* add Edge, Safari and Opera support
* add random config i.e. windows is more common than linux

Specs:
* https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent/Firefox
* http://msdn.microsoft.com/en-us/library/ms537503(VS.85).aspx
* https://developer.chrome.com/multidevice/user-agent
* http://www.javascriptkit.com/javatutors/navigator.shtml

Release history:
* https://en.wikipedia.org/wiki/Firefox_release_history
* https://en.wikipedia.org/wiki/Google_Chrome_release_history
* https://en.wikipedia.org/wiki/Internet_Explorer_version_history

Lists of user agents:
* http://www.useragentstring.com/
* http://www.user-agents.org/
* http://www.webapps-online.com/online-tools/user-agent-strings

"""
# pylint: enable=line-too-long

from random import choice, randint
from datetime import datetime, timedelta

import six

from .warning import warn

__all__ = ['generate_user_agent', 'generate_navigator',
           'generate_navigator_js',
           'UserAgentRuntimeError', 'UserAgentInvalidRequirements']

OS_PLATFORM = {
    'win': (
        'Windows NT 5.1', # Windows XP
        'Windows NT 6.1', # Windows 7
        'Windows NT 6.2', # Windows 8
        'Windows NT 6.3', # Windows 8.1
        'Windows NT 10.0', # Windows 10
    ),
    'mac': (
        'Macintosh; Intel Mac OS X 10.8',
        'Macintosh; Intel Mac OS X 10.9',
        'Macintosh; Intel Mac OS X 10.10',
        'Macintosh; Intel Mac OS X 10.11',
        'Macintosh; Intel Mac OS X 10.12',
    ),
    'linux': (
        'X11; Linux',
        'X11; Ubuntu; Linux',
    ),
    #'android': (
    #    'Android 4.4', # 2013-10-31
    #    'Android 5.0', # 2014-11-12
    #    'Android 6.0', # 2015-10-05
    #),
}

OS_CPU = {
    'win': (
        '', # 32bit
        'Win64; x64', # 64bit
        'WOW64', # 32bit process on 64bit system
    ),
    'linux': (
        'i686', # 32bit
        'x86_64', # 64bit
        'i686 on x86_64', # 32bit process on 64bit system
    ),
    'mac': (
        '',
    ),
}

OS_NAVIGATORS = {
    'win': ('chrome', 'firefox', 'ie'),
    'mac': ('firefox', 'chrome'),
    'linux': ('chrome', 'firefox'),
    'android': ('firefox',),
}

NAVIGATOR_OSES = {
    'chrome': ('win', 'linux', 'mac'),
    'firefox': ('win', 'linux', 'mac'),
    'ie': ('win',),
}

NAVIGATOR = ('firefox', 'chrome', 'ie')
FIREFOX_VERSION = (
    ('45.0', datetime(2016, 3, 8)),
    ('46.0', datetime(2016, 4, 26)),
    ('47.0', datetime(2016, 6, 7)),
    ('48.0', datetime(2016, 8, 2)),
    ('49.0', datetime(2016, 9, 20)),
    ('50.0', datetime(2016, 11, 15)),
    ('51.0', datetime(2017, 1, 24)),
)
CHROME_BUILD = (
    (49, 2623, 2660), # 2016-03-02
    (50, 2661, 2703), # 2016-04-13
    (51, 2704, 2742), # 2016-05-25
    (52, 2743, 2784), # 2016-07-20
    (53, 2785, 2839), # 2016-08-31
    (54, 2840, 2882), # 2016-10-12
    (55, 2883, 2923), # 2016-12-01
    (56, 2924, 2986), # 2016-12-01
)
IE_VERSION = (
    # (numeric ver, string ver, trident ver) # release year
    (8, 'MSIE 8.0', '4.0'), # 2009
    (9, 'MSIE 9.0', '5.0'), # 2011
    (10, 'MSIE 10.0', '6.0'), # 2012
    (11, 'MSIE 11.0', '7.0'), # 2013
)
USER_AGENT_TEMPLATE = {
    'firefox': (
        'Mozilla/5.0'
        ' ({system[platform]}; rv:{app[build_version]})'
        ' Gecko/{app[geckotrail]}'
        ' Firefox/{app[build_version]}'
    ),
    'chrome': (
        'Mozilla/5.0'
        ' ({system[platform]}) AppleWebKit/537.36'
        ' (KHTML, like Gecko)'
        ' Chrome/{app[build_version]} Safari/537.36'
    ),
    'ie_less_11': (
        'Mozilla/5.0'
        ' (compatible; {app[build_version]}; {system[platform]};'
        ' Trident/{app[trident_version]})'
    ),
    'ie_11': (
        'Mozilla/5.0'
        ' ({system[platform]}; Trident/{app[trident_version]};'
        ' rv:11.0) like Gecko'
    ),
}


class UserAgentRuntimeError(Exception):
    pass


class UserAgentInvalidRequirements(UserAgentRuntimeError):
    pass


def get_firefox_build():
    build_ver, date_from = choice(FIREFOX_VERSION)
    try:
        idx = FIREFOX_VERSION.index((build_ver, date_from))
        _, date_to = FIREFOX_VERSION[idx + 1]
    except IndexError:
        date_to = date_from + timedelta(days=1)
    sec_range = (date_to - date_from).total_seconds() - 1
    build_rnd_time = (date_from +
                      timedelta(seconds=randint(0, sec_range)))
    return build_ver, build_rnd_time.strftime('%Y%m%d%H%M%S')



def get_chrome_build():
    build = choice(CHROME_BUILD)
    return '%d.0.%d.%d' % (
        build[0],
        randint(build[1], build[2]),
        randint(0, 99),
    )


def get_ie_build():
    """
    Return random IE version as tuple
    (numeric_version, us-string component)

    Example: (8, 'MSIE 8.0')
    """

    return choice(IE_VERSION)


MACOSX_CHROME_BUILD_RANGE = {
    # https://en.wikipedia.org/wiki/MacOS#Release_history
    '10.8': (0, 8),
    '10.9': (0, 5),
    '10.10': (0, 5),
    '10.11': (0, 6),
    '10.12': (0, 2)
}


def fix_chrome_mac_platform(platform):
    """
    Chrome on Mac OS adds minor version number and uses underscores instead
    of dots. E.g. platform for Firefox will be: 'Intel Mac OS X 10.11'
    but for Chrome it will be 'Intel Mac OS X 10_11_6'.

    :param platform: - string like "Macintosh; Intel Mac OS X 10.8"
    :return: platform with version number including minor number and formatted
    with underscores, e.g. "Macintosh; Intel Mac OS X 10_8_2"
    """
    ver = platform.split('OS X ')[1]
    build_range = range(*MACOSX_CHROME_BUILD_RANGE[ver])
    build = choice(build_range)
    mac_ver = ver.replace('.', '_') + '_' + str(build)
    return 'Macintosh; Intel Mac OS X %s' % mac_ver


def build_system_components(os_name, navigator_name):
    """
    For given os_name build random platform and oscpu
    components

    Returns dict {platform, oscpu}
    """

    if os_name == 'win':
        base_platform = choice(OS_PLATFORM['win'])
        cpu = choice(OS_CPU['win'])
        if cpu:
            platform = '%s; %s' % (base_platform, cpu)
        else:
            platform = base_platform
        res = {
            'platform': platform,
            'oscpu': platform,
        }
    elif os_name == 'linux':
        cpu = choice(OS_CPU['linux'])
        base_platform = choice(OS_PLATFORM['linux'])
        res = {
            'platform': '%s %s' % (base_platform, cpu),
            'oscpu': 'Linux %s' % cpu,
        }
    elif os_name == 'mac':
        cpu = choice(OS_CPU['mac'])
        platform = choice(OS_PLATFORM['mac'])
        if navigator_name == 'chrome':
            platform = fix_chrome_mac_platform(platform)
        res = {
            'platform': platform,
            'oscpu': 'Intel Mac OS X %s' % platform.split(' ')[-1],
        }
    #elif os_name == 'android':
    #    pass
    return res


def build_app_components(os_id, navigator_id):
    """
    For given navigator_id build app features

    Returns dict {name, product_sub, vendor, build_version, build_id}
    """

    if navigator_id == 'firefox':
        build_version, build_id = get_firefox_build()
        if os_id in ('win', 'linux', 'mac'):
            geckotrail = '20100101'
        else:
            geckotrail = build_version
        res = {
            'name': 'Netscape',
            'product_sub': '20100101',
            'vendor': '',
            'build_version': build_version,
            'build_id': build_id,
            'geckotrail': geckotrail,
        }
    elif navigator_id == 'chrome':
        res = {
            'name': 'Netscape',
            'product_sub': '20030107',
            'vendor': 'Google Inc.',
            'build_version': get_chrome_build(),
            'build_id': None,
        }
    elif navigator_id == 'ie':
        num_ver, build_version, trident_version = get_ie_build()
        if num_ver >= 11:
            app_name = 'Netscape'
        else:
            app_name = 'Microsoft Internet Explorer'
        app_product_sub = None
        app_vendor = ''
        res = {
            'name': app_name,
            'product_sub': None,
            'vendor': '',
            'build_version': build_version,
            'build_id': None,
            'trident_version': trident_version,
        }
    return res


def pickup_os_navigator_ids(os, navigator):
    """
    Select one random pair (os_id, navigator_id) from all
    possible combinations matching the given os and
    navigator filters.

    :param os: allowed os(es)
    :type os: string or list/tuple or None
    :param navigator: allowed browser engine(s)
    :type navigator: string or list/tuple or None
    """

    # Process os option
    if isinstance(os, six.string_types):
        os_choices = [os]
    elif isinstance(os, (list, tuple)):
        os_choices = list(os)
    elif os is None:
        os_choices = list(OS_PLATFORM.keys())
    else:
        raise UserAgentRuntimeError('Option os has invalid'
                                    ' value: %s' % os)
    for item in os_choices:
        if item not in OS_NAVIGATORS:
            raise UserAgentRuntimeError('Invalid os option: %s' % item)

    # Process navigator option
    if isinstance(navigator, six.string_types):
        navigator_choices = [navigator]
    elif isinstance(navigator, (list, tuple)):
        navigator_choices = list(navigator)
    elif navigator is None:
        navigator_choices = list(NAVIGATOR)
    else:
        raise UserAgentRuntimeError('Option navigator has invalid'
                                    ' value: %s' % navigator)
    for item in navigator_choices:
        if item not in NAVIGATOR_OSES:
            raise UserAgentRuntimeError('Invalid navigator option: %s' % item)

    # If we have only one navigator option to choose from
    # Then use it and select os from oses
    # available for choosen navigator
    if len(navigator_choices) == 1:
        navigator_id = navigator_choices[0]
        avail_os_choices = [x for x in os_choices
                                  if x in NAVIGATOR_OSES[navigator_id]]
        # This list could be empty because of invalid
        # parameters passed to the `generate_navigator` function
        if avail_os_choices:
            os_id = choice(avail_os_choices)
        else:
            os_list = '[%s]' % ', '.join(avail_os_choices)
            navigator_list = '[%s]' % ', '.join(navigator_choices)
            raise UserAgentInvalidRequirements(
                'Could not generate navigator for any combination of'
                ' %s oses and %s navigators'
                % (os_list, navigator_list))
    else:
        os_id = choice(os_choices)
        avail_navigator_choices = [x for x in navigator_choices
                                   if x in OS_NAVIGATORS[os_id]]
        # This list could be empty because of invalid
        # parameters passed to the `generate_navigator` function
        if avail_navigator_choices:
            navigator_id = choice(avail_navigator_choices)
        else:
            os_list = '[%s]' % ', '.join(avail_os_choices)
            navigator_list = '[%s]' % ', '.join(navigator_choices)
            raise UserAgentInvalidRequirements(
                'Could not generate navigator for any combination of'
                ' %s oses and %s navigators'
                % (os_list, navigator_list))

    assert os_id in OS_PLATFORM
    assert navigator_id in NAVIGATOR

    return os_id, navigator_id


def generate_navigator(os=None, navigator=None, platform=None):
    """
    Generates web navigator's config

    :param os: limit list of oses for generation
    :type os: string or list/tuple or None
    :param navigator: limit list of browser engines for generation
    :type navigator: string or list/tuple or None
    :return: User-Agent config
    :rtype: dict with keys (os, name, platform, oscpu, build_version,
                            build_id, app_version, app_name, app_code_name,
                            product, product_sub, vendor, vendor_sub,
                            user_agent)
    :raises UserAgentInvalidRequirements: if could not generate user-agent for
        any combination of allowed platforms and navigators
    :raise UserAgentRuntimeError: if any of passed options is invalid
    """
    
    if platform is not None:
        os = platform
        warn('The `platform` option is deprecated.'
             ' Use `os` option instead.', stacklevel=3)
    os_id, navigator_id = pickup_os_navigator_ids(os, navigator)
    system = build_system_components(os_id, navigator_id)
    app = build_app_components(os_id, navigator_id)
    if navigator_id == 'ie':
        tpl_name = ('ie_11' if app['build_version'] == 'MSIE 11.0'
                    else 'ie_less_11')
    else:
        tpl_name = navigator_id
    ua_template = USER_AGENT_TEMPLATE[tpl_name]
    user_agent = ua_template.format(system=system, app=app)
    app_version = None
    if navigator_id in ('chrome', 'ie'):
        assert user_agent.startswith('Mozilla/')
        app_version = user_agent.split('Mozilla/', 1)[1]
    elif navigator_id == 'firefox':
        os_token = {
            'win': 'Windows',
            'mac': 'Macintosh',
            'linux': 'X11',
        }[os_id]
        app_version = '5.0 (%s)' % os_token
    assert app_version is not None

    return {
        # ids
        'os_id': os_id,
        'navigator_id': navigator_id,
        # system components
        'platform': system['platform'],
        'oscpu': system['oscpu'],
        # app components
        'build_version': app['build_version'],
        'build_id': app['build_id'],
        'app_version': app_version,
        'app_name': app['name'],
        'app_code_name': 'Mozilla',
        'product': 'Gecko',
        'product_sub': app['product_sub'],
        'vendor': app['vendor'],
        'vendor_sub': '',
        # compiled user agent
        'user_agent': user_agent,
    }


def generate_user_agent(os=None, navigator=None, platform=None):
    """
    Generates HTTP User-Agent header

    :param os: limit list of os for generation
    :type os: string or list/tuple or None
    :param navigator: limit list of browser engines for generation
    :type navigator: string or list/tuple or None
    :return: User-Agent string
    :rtype: string
    :raises UserAgentInvalidRequirements: if could not generate user-agent for
        any combination of allowed oses and navigators
    :raise UserAgentRuntimeError: if any of passed options is invalid
    """
    return generate_navigator(os=os, navigator=navigator,
                              platform=platform)['user_agent']


def generate_navigator_js(os=None, navigator=None, platform=None):
    """
    Generates web navigator's config with keys corresponding
    to keys of `windows.navigator` JavaScript object.

    :param os: limit list of oses for generation
    :type os: string or list/tuple or None
    :param navigator: limit list of browser engines for generation
    :type navigator: string or list/tuple or None
    :return: User-Agent config
    :rtype: dict with keys (TODO)
    :raises UserAgentInvalidRequirements: if could not generate user-agent for
        any combination of allowed oses and navigators
    :raise UserAgentRuntimeError: if any of passed options is invalid
    """

    config = generate_navigator(os=os, navigator=navigator,
                                platform=platform)
    return {
        'appCodeName': config['app_code_name'],
        'appName': config['app_name'],
        'appVersion': config['app_version'],
        'platform': config['platform'],
        'userAgent': config['user_agent'],
        'oscpu': config['oscpu'],
        'product': config['product'],
        'productSub': config['product_sub'],
        'vendor': config['vendor'],
        'vendorSub': config['vendor_sub'],
        'buildID': config['build_id'],
    }
