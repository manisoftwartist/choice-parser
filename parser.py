
import re

from question import Question

########################################################################
class Parser(object):
    """
    The parser breaks up a string into tokens and then looks through those
    tokens to determine what is the stem and what are the options.
    """
    def __init__(self):
        pass

    def _tokenize(self, string):
        """
        Split input string into tokens based on line-breaks.

        @param  string  The input string
        @return  list  The tokenized input
        """
        tokens = []

        # Split and strip the input string by newlines
        for token in re.split('(.*)', string):
            if token.strip() != '':
                tokens.append(token)

        return tokens

    def _chunk(self, string):
        """
        Split input string into tokens based on option groups.  In other
        words we look for a group of lines that start with A, B, C and
        maybe D and then assume the stem is the bit before each.

        @param  string  The input string
        @return  list  The tokenized input
        """
        a = '(?:A\.?|\(A\))'
        b = '(?:B\.?|\(B\))'
        c = '(?:C\.?|\(C\))'
        d = '(?:D\.?|\(D\))'
        e = '(?:E\.?|\(E\))'
        l = '[^\n\r]+\n\s*'
        s = '\s+'
        #              A.          B.          C.             D.
        regex = r"(\s*{a}{s}{line}{b}{s}{line}{c}{s}{line}(?:{d}{s}{line})(?:{e}{s}{line})?)".format(
            a=a, b=b, c=c, d=d, e=e, line=l, s=s
            )
        p = re.compile(regex, re.IGNORECASE)

        return p.split(string)

########################################################################
class SingleParser (Parser):
    """
    The single parser assumes only one question and takes the first token
    to be the stem and the rest of the tokens are the options.

    >>> from parser import SingleParser
    >>> i = '''This is the stem
    ... This is the first option
    ... This is the second option
    ... '''
    >>> p = SingleParser()
    >>> q = p.parse(i)[0]
    >>> len(q.options)
    2
    """
    def __init__(self):
        super(SingleParser, self).__init__()

    def parse(self, string):
        tokens = self._tokenize(string)
        if not tokens: return []

        question = Question()
        question.stem = tokens[0]
        question.options = tokens[1:] if len(tokens) > 1 else []

        return [question]

########################################################################
class IndexParser (Parser):
    """
    The index parser determines stems to be prefixed with numbers and the
    options to be prefixed with letters.

    >>> from router import Router
    >>> r = Router()
    >>> r.setup(['-i', 'input/anarchy'])
    >>> i = r.get_input()
    >>> Q = IndexParser().parse(i)
    >>> len(Q)
    10
    """
    def __init__(self):
        super(IndexParser, self).__init__()

    def parse(self, string):
        """
        Spin thru the tokens and create a list of Questions.

        @param  string  The input string to parse
        @return  list  The parsed Question objects
        """
        questions = []
        question = None

        for token in self._tokenize(string):
            s = re.match(r"^\s*\d+\.\s", token)
            if s and s.group():
                if question and len(question.options) > 0:
                    questions.append(question)
                question = Question()
                question.stem = token
                continue

            o = re.match(r"^\s*[a-zA-Z][.)]\s", token)
            if o and o.group():
                try:
                    assert question is not None
                    question.options.append(token)

                except AssertionError:
                    pass

        if question and len(question.options) > 0:
            questions.append(question)

        return questions

########################################################################
class BlockParser (Parser):
    """
    The block parser determines stems to be all the text in between the
    options.

    >>> from router import Router
    >>> r = Router()
    >>> r.setup(['-i', 'input/drivers'])
    >>> i = r.get_input()
    >>> Q = BlockParser().parse(i)
    >>> len(Q)
    11
    """
    def __init__(self):
        super(BlockParser, self).__init__()

    def parse(self, string):
        """
        Spin thru the tokens and create a list of Questions.

        @param  string  The input string to parse
        @return  list  The parsed Question objects
        """
        questions = []
        question = Question()
        option = False

        for token in self._tokenize(string):
            o = re.match(r"^\s*[a-zA-Z][.)] ", token)
            if o and o.group():
                option = True
                try:
                    assert question is not None
                    question.options.append(token)
                except AssertionError:
                    pass
                continue

            if option:
                questions.append(question)
                question = Question()
                question.stem = ''
                option = False

            try:
                assert question is not None
                question.stem += token + '\n'
            except AssertionError:
                pass

        if question and len(question.options) > 0:
            questions.append(question)

        return questions

########################################################################
class ChunkParser (Parser):
    """
    The chunnk parser does not tokenize by lines but instead by groups of
    lines separated by the option list; therefore, every other entry in
    the split list consists of, theoretically, the stem followed by the
    option list in the following entry which then is split line by line
    for the individual options.

    >>> from router import Router
    >>> r = Router()
    >>> i = '''3. What is the name of the part that contains the question?
    ... A.     Multiple
    ... B.     Choice
    ... C.     Problem
    ... D.     Stem
    ... '''
    >>> p = ChunkParser()
    >>> Q = p.parse(i)
    >>> len(Q)
    1
    >>> len(Q[0].options)
    4
    """
    def __init__(self):
        super(ChunkParser, self).__init__()

    def parse(self, string):
        """
        Spin thru the chunks and create a list of Questions.

        @param  string  The input string to parse
        @return  list  The parsed Question objects
        """
        questions = []
        question  = None
        re_index  = r'(?:[A-Za-z]\.?|\([A-Za-z]\))'
        re_body   = r'[^\n]+'
        re_option = r'(\s*{index}\s+{body}\s*)'.format(index=re_index, body=re_body)
        chunks = self._chunk(string)

        # spin thru the input chunks two at a time, the first being the
        # stem, presumably, and the second being the option group
        for st_index in range(0, len(chunks), 2):
            op_index = st_index +1
            question = Question()
            stem = re.search(r"\n*(.+)$", chunks[st_index])
            if stem:
                question.stem = stem.group().strip()

                if op_index < len(chunks):
                    options = [o.strip() for o in re.split(re_option, chunks[op_index]) if o]
                    #import pdb; pdb.set_trace()
                    for option in options:
                        question.options.append(option)

                    questions.append(question)

        return questions
