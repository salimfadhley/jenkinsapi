import re
import collections

Token = collections.namedtuple('Token', ['typ', 'value'])
indent = ""

class LabelExpression(object):
    """
    LabelExpression takes the label expression as defined in the <assignedNode> element and parses it.
    The resulting object can be used to determine if a set of labels meet the criteria defined by the expression.
    """

    # The spec defines how to match id's and operators in the given expression
    _spec =  [
        ('GROUP',   r'\(.*\)'),
        ('NOT',     r'!'),
        ('OR',      r'\|\|'),
        ('AND',     r'&&'),
        ('IMPLY',   r'->'),
        ('ONLYIF',  r'<->'),
        ('SKIP',    r'[ \t]+'),
        ('ID',      r'[\w-]+(?!>)')
    ]

    # The order operations should be performed in. Highest first.
    _precedence = {
        'GROUP':  5,
        'NOT':    4,
        'AND':    3,
        'OR':     2,
        'IMPLY':  1,
        'ONLYIF': 0
    }

    # Assemble the spec into a long regex, and compile it
    _tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in _spec)
    _get_token = re.compile(_tok_regex).match

    def __init__(self, expr):
        self.expr = expr
        self.tokens = self._gen_tokens(expr, init=True)

    def __str__(self):
        return self.expr

    def __repr__(self):
        return "<Jenkins LabelExpression %s>" % self.expr

    def _tokenize(self, expr):
        # Generator that yeilds the tokens of the expression.
        pos = 0
        matchobj = self._get_token(expr)
        while matchobj is not None:
            typ = matchobj.lastgroup
            val = matchobj.group(typ)
            if typ == 'GROUP':
                val = self._gen_tokens(val[1:-1])
            if typ != 'SKIP':
                yield Token(typ, val)
            pos = matchobj.end()
            matchobj = self._get_token(expr, pos)

    def _gen_tokens(self, expr, init=False):
        # Iterate over the tokens, returning a list when init is True or the number of tokens yielded is > 1
        l = [t for t in self._tokenize(expr)]
        if len(l) == 1 and init == False:
            return l[0]
        return l

    def matches(self, labels):
        """
        Returns True or False.

        This works by Substituting labels from the list :param labels: where they match ID tokens with True,
        and all ID tokens not matching with False. When an operator token is encountered and it can be evaluated it
        will be evaluated and the operator and operands replaced with the result, gradually shrinking a copy of our
        tokens down to a single result.

        For example given the expression "(foo||bar)&&baz" and the list of labels ["foo"] the expression becomes
        "(True||False)&&False)" which can then be reduced to "False||False" which finally returns False

        As the expression is reduced an optional precedence value is passed to indicate the precedence of the operator
        from which the reduce function was called. This helps us determine when to reduce an expression to the left or
        right of an operator.
        """

        if type(labels) != list:
            labels = [labels]

        # In the case of a single Token assume an ID and return whether or not it is in the list of labels.
        if len(self.tokens) == 1 and type(self.tokens[0]) == Token:
            return self.tokens[0].value in labels

        # Start with a copy of self.tokens
        tokens = [] + self.tokens

        TRUTH = (True, False)

        def skip_operation(current_operation, tokens):
            """
            Look in tokens for operations of higher precedence than current_operation.
            Returns True if current_operation should be skipped, False otherwise.
            """
            for token in tokens:
                if type(token) == Token and self._precedence[token.typ] > self._precedence[current_operation]:
                    return True
            return False

        def reduce(tokens):
            x = 0
            while len(tokens) > 1:
                # The lenth of tokens is a moving target, make sure we start from the beginning on each pass.
                if x >= len(tokens):
                    x = 0

                # Skip over Tokens that have already been reduced to a boolean value.
                if type(tokens[x]) == Token:
                    if tokens[x].typ == 'ID':
                        # Swap an ID token with True if the label exists in labels, or False
                        tokens[x] = tokens[x].value in labels

                    elif tokens[x].typ == 'GROUP':
                        # Evaluate the expression inside a group down to a single bool and replace the GROUP token
                        # with the result
                        left = tokens[:x]
                        right = tokens[x + 1:]
                        # Make sure we don't mutate the original list inside a GROUP token by passing a copy to reduce
                        tokens = left + [reduce([] + tokens[x].value)] + right

                    elif tokens[x].typ == 'NOT':
                        # If the next token is a bool replace tokens[x:x+2] with !tokens[x+1]. Since NOT is second
                        # only to group it is safe to assume that only a single token to the right needs to be inverted,
                        # since in a valid expression the element to the right will be an ID or a GROUP which should
                        # already be reduced.
                        if tokens[x + 1] in TRUTH:
                            if len(tokens) == 2:
                                tokens = [not tokens[x + 1]]
                                break
                            else:
                                left = tokens[:x]
                                right = []
                                if x + 1 < len(tokens) - 1:
                                    right = tokens[x + 2:]
                                tokens = tokens[:x] + [not tokens[x + 1]] + right

                    elif tokens[x].typ == 'AND':
                        # if the previous and next elements are boolean replace tokens[x-1:x+2] with the AND of those
                        # elements
                        if (tokens[x - 1] in TRUTH) and (tokens[x + 1] in TRUTH):
                            if len(tokens) == 3:
                                tokens = [tokens[x - 1] and tokens[x + 1]]
                                break
                            else:
                                left = tokens[:x - 1]
                                right = tokens[x + 2:]
                                # if the next operation is of higher precedence, do it first. (GROUP or NOT)
                                if not skip_operation('AND', right):
                                    tokens = left + [tokens[x - 1] and tokens[x + 1]] + right

                    elif tokens[x].typ == 'OR':
                        # if the last and next elements are boolean replace tokens[x-1:x+2] with the or of those
                        # elements
                        if tokens[x - 1] in TRUTH and tokens[x + 1] in TRUTH:
                            if len(tokens) == 3:
                                tokens = [tokens[x - 1] or tokens[x + 1]]
                                break
                            else:
                                left = tokens[:x - 1]
                                right = tokens[x + 2:]
                                # if the next operation is of higher precedence, do it first. (GROUP, NOT or AND)
                                if not skip_operation('OR', right):
                                    tokens = left + [tokens[x - 1] or reduce([tokens[x + 1]] + right)]

                    elif tokens[x].typ == 'IMPLY':
                        # IMPLY: the expression 'a->b' translates to "if 'a' matches then 'b' must also match".
                        # In boolean this translates to '!a || b' so it is legal to have b with out a but not
                        # the other way around.
                        if tokens[x - 1] in TRUTH and tokens[x + 1] in TRUTH:
                            if len(tokens) == 3:
                                tokens = [not tokens[x - 1] or tokens[x + 1]]
                                break
                            else:
                                left = tokens[:x - 1]
                                right = tokens[x + 2:]
                                if not skip_operation('IMPLY', right):
                                    tokens = left + [not tokens[x - 1] or reduce([tokens[x+1]] + right)]

                    elif tokens[x].typ == 'ONLYIF':
                        # ONLYIF: the expression 'a<->b' translates to: "if 'a' matches, 'b' must also match, but if
                        # 'a' does not match, 'b' must also not match.", or in boolean "a && b || !a && !b".
                        if tokens[x - 1] in TRUTH and tokens [x + 1] in TRUTH:
                            if len(tokens) == 3:
                                a = tokens[x - 1]
                                b = tokens[x + 1]
                                tokens = [a and b or not a and not b]
                            else:
                                left = tokens[:x - 1]
                                right = tokens[x + 1:]
                                if not skip_operation('ONLYIF', right):
                                    a = tokens[x - 1]
                                    # Since we have no higher-precedence operators to the right we can safely reduce
                                    # The right hand and use it as 'b'. The only operation left to be reduced would
                                    # be another ONLYIF.
                                    b = reduce(right)
                                    tokens = left + [a and b or not a and not b]
                    else:
                        # Unknown condition, assume False
                        tokens = [False]
                x += 1
            # When we have only one element left, that is our answer.
            return tokens[0]

        return reduce(tokens)

