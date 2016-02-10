import re
from logging import getLogger

class Tokens:
    token_exemplars = {
        '%tracknumber%' : '(\d+?)', 
        '%title%' : '(.+)',
        '%discnumber%' : '(\d+?)'
    }
    def __init__(self, t):
        self.tx_tokens_to_regexp(t)

    def tx_tokens_to_regexp(self, t):
        log = getLogger('Rkive.MusicFiles')
        token_index = []
        token_count = 0
        token_regexp = tokens
        for token, regexp in self.token_exemplars.iteritems():
            log.info("token: {0}".format(token))
            if token in tokens:
                token_regexp = token_regexp.replace(token, regexp)
                tl = len(token) -1 
                self.token_index.append(token[1:tl])
                log.debug("regxp {0}".format(token_regexp))
        self.token_index = token_index
        token_regexp = re.compile(token_regexp)
        self.regexp = token_regexp
        return token_regexp

    def match(self, parent, s):
        log = getLogger('Rkive.MusicFiles')
        matches = self.regexp.match(s)
        if matches.groups<1:
            log.warn("no matches for {0}".format(s))
            return
        for i in range(0,matches.groups):
            token_name = self.token_index[i]
            token_value = matches.groups(i)
            setattr(parent, token_name, token_value)
