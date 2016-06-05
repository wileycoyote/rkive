
class Movie(object):
    def __init__(self, m, d, y):
        self.movie = m
        self.director = d
        self.year = y

    def p(self):
        print("movie: {0}; director: {1}; year: {2}".
                format(self.movie,self.director, self.year))

