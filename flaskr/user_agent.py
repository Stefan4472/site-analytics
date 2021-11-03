def is_bot(user_agent: str) -> bool:
    # No user agent: suspect bot
    if not user_agent:
        return True
    elif 'bot' in user_agent.lower():
        return True
    elif 'scan' in user_agent.lower():
        return True
    elif 'request' in user_agent.lower():
        return True
    return False


def determine_os(user_agent: str) -> str:
    if 'Windows' in user_agent:
        return 'Windows'
    elif 'Linux' in user_agent:
        return 'Linux'
    elif 'Mac' in user_agent:
        return 'Mac'
    else:
        return ''


def determine_browser(user_agent: str) -> str:
    # Note: this makes no sense for bots, which usually list a bunch
    # of "compatible" browsers
    if 'Chrome' in user_agent:
        return 'Chrome'
    elif 'Firefox' in user_agent:
        return 'Firefox'
    elif 'Safari' in user_agent:
        return 'Safari'
    else:
        return ''
