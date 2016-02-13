import re
from logging import getLogger

class Regexp:
    token_exemplars = {
        '%tracknumber%' : '(\d+)', 
        '%title%' : '(.+)',
        '%discnumber%' : '(\d+?)'
    }
    def __init__(self, t):
        self.token_index = []
        self.regexp = ""
        self.tx_tokens_to_regexp(t)

    def tx_tokens_to_regexp(self, tokens):
        log = getLogger('Rkive.MusicFiles')
        token_count = 0
        token_regexp = tokens
        log.info("tokens: {0}".format(tokens))
        for token, regexp in self.token_exemplars.iteritems():
            if token in token_regexp:
                token_regexp = token_regexp.replace(token, regexp)
                tl = len(token) -1 
                self.token_index.append(token[1:tl])
        log.info("regxp {0}".format(token_regexp))
        self.regexp = re.compile(token_regexp)
        return token_regexp

    def match(self, s):
        log = getLogger('Rkive.MusicFiles')
        matches = self.regexp.match(s)
        if not matches:
            log.warn("no matches for {0}".format(s))
            return
        tokens = {}
        i = 0
        for group in matches.groups():
            log.debug("token_index: {0}".format(self.token_index[i]))
            log.debug("group: {0}".format(group))
            token_name = self.token_index[i]
            tokens[token_name] = group
            i = i + 1
        return tokens
