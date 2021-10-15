import os

from colorama import Fore, Style


class Parser:
    __is_init = False
    __number = 0
    _user_agents_list = []
    _proxies_list = []

    def __new__(cls, *args, **kwargs):
        cls.__number += 1
        print(Fore.YELLOW + f'[INFO]  start {cls.__name__}', Fore.CYAN + f'{cls.__number}')
        if not cls.__is_init:
            cls.__is_init = True
            cls._set_variables()
        instance = super(Parser, cls).__new__(cls)
        return instance

    def __init__(self):
        super(Parser, self).__init__()
        self._current_proxy = None
        self._proxies = [proxy for proxy in self._proxies_list]
        self._encoding = 'utf-8'
        self._max_retry = 5
        self._except_print = False

    @classmethod
    def _set_variables(cls):
        if os.path.exists(os.getcwd() + '/text_files/user-agents.txt'):
            cls._user_agents_list = cls.__get_user_agents_list()
        else:
            print(Fore.YELLOW + '[INFO]', Style.RESET_ALL +
                  f' user-agent.txt - not found, by default the user_agent module will be used for generation.')
        if os.path.exists(os.getcwd() + '/text_files/proxies.txt'):
            cls._proxies_list = cls.__get_proxies_list()
        else:
            print(Fore.YELLOW + '[INFO]', Style.RESET_ALL +
                  f' proxies.txt - not found, using a proxy is not possible.')

    @classmethod
    def __get_user_agents_list(cls):
        ua_list = open('text_files/user-agents.txt').read().strip().split('\n')
        for ua in ua_list:
            if len(ua) == 0:
                ua_list.remove(ua)
        print(Fore.YELLOW + '[INFO]', Style.RESET_ALL + f' user agent list count: ' + Fore.CYAN + f'{len(ua_list)}')
        return ua_list

    @classmethod
    def __get_proxies_list(cls):
        p_list = open('text_files/proxies.txt').read().strip().split('\n')
        for p in p_list:
            if len(p) == 0:
                p_list.remove(p)
        print(Fore.YELLOW + '[INFO]', Style.RESET_ALL + f' proxies list count: ' + Fore.CYAN + f'{len(p_list)}')
        return p_list

    @classmethod
    def set_marker(cls, marker: str):
        if marker:
            print(Fore.YELLOW + f'[INFO]  {cls.__name__}', Fore.MAGENTA + f' {marker}')

    @property
    def current_proxy(self):
        return self._current_proxy

    @property
    def max_retry(self):
        return self._max_retry

    @property
    def encoding(self):
        return self._encoding

    @property
    def except_print(self):
        return self._except_print

