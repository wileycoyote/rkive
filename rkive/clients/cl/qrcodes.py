from cv2 import imread
import zbar
import isbnlib
import os
from rkive.index.books import Book


class QRCode(object):
    map = {
        'ISBN-13': 'isbn13',
        'Title': 'title',
        'Authors': 'authors',
        'Publisher': 'publisher',
        'Year': 'year',
        'Language': 'language'
    }

    def read(self, file):
        """ Read the file """
        img = imread(file, 0)
        scanner = zbar.Scanner()
        results = scanner.scan(img)
        for r in results:
            isbn = r.data

        meta = isbnlib.meta(str(isbn), service='default', cache='default')
        meta_std = dict()
        for k, v in meta.items():
            if k not in self.map:
                print(f"Unknown isbn key {k}")
                continue
            mapped_key = self.map[k]
            meta_std[mapped_key] = v
        return Book(**meta_std)


if __name__ == '__main__':
    QRCODES = './data/qrcodes/'
    qrc = QRCode()
    for q in os.listdir(QRCODES):
        if not q.lower().endswith('.png'):
            continue
        fp = os.path.join(QRCODES, q)
        data = qrc.read(fp)
        print(data)
