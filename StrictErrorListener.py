from antlr4.error.ErrorListener import ErrorListener

class StrictErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise Exception(f"Syntax error at {line}:{column} - {msg}")
