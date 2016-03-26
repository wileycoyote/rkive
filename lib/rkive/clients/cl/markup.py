from rkive.clients.cl.opts import GetOpts, FileValidation
import rkive.clients.log
import argparse
from logging import getLogger
import sys

class MarkupClient(GetOpts):

    def run(self, logloc=None):
        try:
            go = GetOpts(parent=self)
            go.p.add_argument('--bare',  type=str, help="data with no markup", action=FileValidation)
            go.p.add_argument('--markup',  type=str, help="marked-up file")
            go.p.add_argument(
                'infile', 
                nargs='?', 
                type=argparse.FileType('r'),
                default=sys.stdin)
            go.p.add_argument(
                'outfile', 
                nargs='?', 
                type=argparse.FileType('w'),
                default=sys.stdout)
            go.get_opts()
            self.console = True
            rkive.clients.log.LogInit().set_logging(location=log, filename='markup.log', debug=self.debug, console=self.console)
            log = getLogger('Rkive.Markup')
            if (self.markup and self.bare):
                self.create_markup(self.bare, self.markup)
                return
            if (self.infile and self.outfile):
                self.create_markup(self.infile, self.outfile)
                return
        except SystemExit:
            pass

    def create_markup(self, inf, out):
        log = getLogger('Rkive')
        log.info("input {0} output {1}".format(inf, out))
        with open(inf,'r') as i, open(out, 'w') as o:
            line_counter = 0
            record = []
            o.write("[")
            header = i.readline().strip().split(',')
            nrrecs = int(header.pop(0))
            size_record = len(header)
            nrlines = nrrecs*size_record
            for l in i:
                line_counter = line_counter + 1
                record.append(l.strip())
                if (line_counter%size_record == 0):
                    fields = []
                    for idx in range(0,size_record):
                        field_name = header[idx]
                        field_value = record[idx]
                        fields.append('"{0}":"{1}"'.format(field_name,field_value))
                    # make sure the record seperator is NOT added at the last record
                    record_s = "{"+",".join(fields)+"}"
                    if (line_counter<nrlines):
                        record_s=record_s+',\n'
                    o.write(record_s)
                    record = []
            o.write("]\n")
       
if __name__ == '__main__':
    Markup().run()
