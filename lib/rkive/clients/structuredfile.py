class Markdown:    

    def read_file(self, inf, funcs=[]):
        log = getLogger('Rkive')
        log.info("input {0} output {1}".format(inf, out))
        with open(inf,'r') as i:
            line_counter = 0
            record = []
            header = i.readline().strip().split(',')
            nrrecs = int(header.pop(0))
            size_record = len(header)
            for l in i:
                line_counter = line_counter + 1
                record.append(l.strip())
                if (line_counter%size_record == 0):
                    func(header, record)
                    record = []

