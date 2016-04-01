import rkive.clients.log

class MarkdownReader(object):
    tag_tx = {'A': 'artist', 'C': 'comment', 'R':'comment', 'P':'comment', 'E':'comment'}
    role = {'A':'', 'C':'', 'R':'Recording', 'P': 'Producer', 'E':'Engineer'}

    def __init__(self, filename):
        self.filename = filename

    def read_record(self, f):
        record = {'tracks':[],'data':[]}
        buffer = record['tracks']
        while True:
            l = f.readline()
            if not l:
                record = None
                break
            l = l.strip()
            if (l=='==='):
                buffer = record['data']
                continue
            buffer.append(l)
        return record

    def readblock(self, f):
        while True:
            data = self.read_record(f)
            if not data:
                break
            yield data
