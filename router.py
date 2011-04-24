
import sys
import argparse

class Router:
    """
    The router collects all the input data and prepares it for parsing.
    """

    # Properties
    # ------------------------------------------------------------------

    # Property: version
    # Router version
    version = "0.1"

    # Property: options
    # Command line arguments
    options = None

    # Property: questions
    # The list of questions
    questions = ''

    # Property: output
    # The rendered output
    output = ''

    # Constructor
    # ------------------------------------------------------------------

    def __init__(self):
        pass

    # Methods
    # ------------------------------------------------------------------

    def parse_args(self, options=sys.argv[1:]):
        global version

        parser = argparse.ArgumentParser(
            description='Parses and tokenizes text.',
            epilog='Refer to the documentation for more detailed information.',
            prog=sys.argv[0],
            )

        parser.add_argument('-v', '--version', action='version',
                            version='%(prog)s Router version ' + self.version,
                            help='print the version information and exit')

        parser.add_argument('-s', '--showstats', action='store_true', 
                            help='print out some statistical information')

        parser.add_argument('input', metavar='INPUT', type=str, nargs='?',
                            help='input string')

        parser.add_argument('--inputfile', type=str, metavar='FILE',
                            help='input file')

        parser.add_argument('--parser', type=str, metavar='PRSR',
                            help='parser class')

        self.options = parser.parse_args(options)

    def start(self):
        #~ import pdb; pdb.set_trace()
        filestr = inputstr = ''

        if self.options.showstats:
            print 'start(): self.options: ', repr(self.options)

        if (self.options.inputfile):
            try:
                f = open(self.options.inputfile, 'rb')
                #self.input = [x.strip() for x in f if x.strip()]
                filestr = f.read()
                f.close()

            except IOError:
                print 'Could not read file.', sys.exc_info()[1]
                self.exit()

        if (self.options.input):
            inputstr = self.options.input

        self.render(('\n'.join((filestr, inputstr))).strip())

    def render(self, str=None):
        try:
            if str:
                lines = str
            else:
                print 'Enter input text (ctrl-D to end)'
                lines = [sys.stdin.read()]
                lines = " ".join(lines)

        except KeyboardInterrupt:
            pass

        # todo: add actual exception handler
        except:
            sys.stderr.write("Reading failed.\n")
            print sys.exc_info()[0]
            print sys.exc_info()[1]
            return

        try:
            if lines:   
                self.parser = self._get_parser(lines)
                #self.parser.load_string(lines)
                self.questions = self.parser.parse()
            
        except AttributeError:
            sys.stderr.write("Could not parse input, bad parser selected.")
            print sys.exc_info()[1]
            return

        if self.options.showstats:
            self.show_stats()

    def show_stats(self):
        #~ import pdb; pdb.set_trace()
        print 'stats: %d questions found.' % len(self.questions)

        for question in self.questions:
            print 'stats: stem is %d bytes long, %d option%s found.' % (
                len(question.stem),
                len(question.options),
                's' if len(question.options) != 1 else ''
                )

    def _get_parser(self, string):
        parser = self.options.parser if self.options.parser else 'SingleParser'
        #~ Parser = type(parser, (), {})
        Parser = self.forname("parser", parser)
        return Parser(string)

    def forname(self, modname, classname):
        """ 
        Returns a class of "classname" from module "modname". 
        reposted by ben snider 
            from http://mail.python.org/pipermail/python-list/2003-March/192221.html
              on http://www.bensnider.com/2008/02/27/dynamically-import-and-instantiate-python-classes/
        """
        module = __import__(modname)
        classobj = getattr(module, classname)
        return classobj
        
    def exit(self):
        sys.exit()
