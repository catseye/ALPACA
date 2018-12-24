import re


class Scanner(object):
    def __init__(self, text):
        self.text = text
        self.token = None
        self.type = None
        self.pos = 0
        self.scan()

    def scan_pattern(self, pattern, type_, token_group=1):
        pattern = r'(' + pattern + r')'
        regexp = re.compile(pattern, flags=re.DOTALL)
        match = regexp.match(self.text, pos=self.pos)
        if not match:
            return False
        else:
            self.type = type_
            self.token = match.group(token_group)
            self.pos += len(match.group(0))
            return True

    def scan(self):
        self.scan_pattern(r'[ \t\n\r]*', 'whitespace')
        while self.text.startswith('/*'):
            self.scan_pattern(r'\/\*.*?\*\/[ \t\n\r]*', 'comment')
        if self.pos >= len(self.text):
            self.token = None
            self.type = 'EOF'
            return
        if self.scan_pattern(r'\.|\;|\,|\(|\)|\{|\}|\=', 'punctuation'):
            return
        if self.scan_pattern(r'[<>^v]+', 'arrow chain'):
            return
        if self.scan_pattern(r'class|state|neighbourhood|is|to|when|me|in|not',
                             'keyword'):
            return
        if self.scan_pattern(r'and|or|xor', 'boolean operator'):
            return
        if self.scan_pattern(r'true|false|guess', 'boolean literal'):
            return
        if self.scan_pattern(r'\d+', 'integer literal'):
            return
        if self.scan_pattern(r'\"(.*?)\"', 'string literal', token_group=2):
            return
        if self.scan_pattern(r'[a-zA-Z][a-zA-Z0-9]*', 'identifier'):
            return
        if self.scan_pattern(r'.', 'unknown character'):
            return
        else:
            raise AssertionError(
                "this should never happen, self.text=(%s), self.pos=(%s)" %
                (self.text, self.pos)
            )

    def scan_playfield(self):
        """Called when the token which introduces the playfield has
        already just been scanned.

        """
        self.scan_pattern(r'[ \t]*', 'whitespace')
        self.scan_pattern(r'[\n\r]', 'eol')
        elems = []
        y = 0
        while self.pos < len(self.text):
            x = 0
            while self.scan_pattern(r'[^\n\r]', 'arbitrary character'):
                #print repr((x, y, self.token))
                elems.append((x, y, self.token))
                x += 1
            self.scan_pattern(r'[\n\r]', 'eol')
            y += 1
        return elems

    def expect(self, token):
        if self.token == token:
            self.scan()
        else:
            raise SyntaxError("Expected '%s', but found '%s'" %
                              (token, self.token))

    def expect_type(self, type):
        self.check_type(type)
        self.scan()

    def on(self, token):
        return self.token == token

    def on_type(self, type):
        return self.type == type

    def check_type(self, type):
        if not self.type == type:
            raise SyntaxError("Expected %s, but found %s ('%s')" %
                              (type, self.type, self.token))

    def consume(self, token):
        if self.token == token:
            self.scan()
            return True
        else:
            return False

    def consume_type(self, type):
        if self.on_type(type):
            token = self.token
            self.scan()
            return token
        else:
            return None
