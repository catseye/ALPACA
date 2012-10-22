import re


class Scanner(object):
    def __init__(self, text):
        self.text = text
        self.token = None
        self.type = None
        self.scan()

    def scan_pattern(self, pattern, type, token_group=1, rest_group=2):
        pattern = r'^(' + pattern + r')(.*?)$'
        match = re.match(pattern, self.text, re.DOTALL)
        if not match:
            return False
        else:
            self.type = type
            self.token = match.group(token_group)
            self.text = match.group(rest_group)
            return True

    def scan(self):
        self.scan_pattern(r'[ \t\n\r]*', 'whitespace')
        while self.text.startswith('/*'):
            self.scan_pattern(r'\/\*.*?\*\/[ \t\n\r]*', 'comment')
        if not self.text:
            self.token = None
            self.type = 'EOF'
            return
        if self.scan_pattern(r'\.|\;|\,|\(|\)|\=', 'punctuation'):
            return
        if self.scan_pattern(r'class|state|neighbourhood|is|to|when|me|in'
                             r'and|or|xor|not|true|false|guess', 'keyword'):
            return
        if self.scan_pattern(r'\d+', 'integer literal'):
            return
        if self.scan_pattern(r'\"(.*?)\"', 'string literal',
                             token_group=2, rest_group=3):
            return
        if self.scan_pattern(r'[a-zA-Z][a-zA-Z0-9]?\%', 'identifier'):
            return
        if self.scan_pattern(r'.', 'unknown character'):
            return
        else:
            raise ValueError("this should never happen, "
                             "self.text=(%s)" % self.text)

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
