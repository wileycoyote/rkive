from logging import getLogger

class Markdown:    

    def read_file(self, inf, funcs=[]):
        log = getLogger('Rkive')
        log.info("input file {0}".format(inf))
        with open(inf,'r') as i:
            line_counter = 0
            record = []
            header = i.readline().strip().split(',')
            size_record = len(int(header[1]))
            for l in i:
                line_counter = line_counter + 1
                record.append(l.strip())
                if (line_counter%size_record == 0):
                    func(header, record)
                    record = []

