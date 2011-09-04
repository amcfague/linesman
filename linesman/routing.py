from routes import Mapper


def make_map():
    m = Mapper(directory="/Users/amcfague/src/git/linesman/linesman/controllers")
    m.connect("/{controller}")
    m.connect("/{controller}/{action}")
    m.connect("/{controller}/{action}/{id}")
    return m
