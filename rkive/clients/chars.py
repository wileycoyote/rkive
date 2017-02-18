from logging import getLogger
table = {
        1076: 'ä',
        1071: 'ß',
        1100: 'ü',
        1094: 'ö',
        1044: 'Ä',
        1068: 'Ü'
        }
def convert_string(s):
    log = getLogger('Rkive.Chars')
    buff = []
    change=False
    for c in s:
        n = ord(c)
        if n<127:
            buff.append(c)
            continue
        if n in table:
            log.debug("n: {0}".format(n))
            buff.append(table[n])
            change=True
        else:
            log.info("String {0}: unknown char {1} with number {2}".format(s,c,n))
    sc = ''.join(buff)
    if change:
        log.debug("Convert string from {0} to {1}".format(s,sc))
    return sc
