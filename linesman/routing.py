from routes import Mapper


def make_map():
    map = Mapper(directory="/Users/amcfague/src/git/linesman/linesman/controllers")
    map.minimization = False
    map.explicit = False

    map.connect("/{controller}")
    map.connect("/{controller}/{action}")
    map.connect("/{controller}/{action}/{id}")

    return map
