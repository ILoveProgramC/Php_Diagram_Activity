import sys
from antlr4 import *
from PhpLexer import PhpLexer
from PhpParser import PhpParser
from MyVisitor import MyVisitor
from StrictErrorListener import StrictErrorListener

def main(argv):
    input_stream = FileStream(argv[1], encoding="utf-8")
    lexer = PhpLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = PhpParser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(StrictErrorListener())
    
    tree = parser.phpBlock()

    

    visitor = MyVisitor()

    try:
        visitor.visit(tree)
    except Exception as e:
        print(f"\nAnaliza prekinuta: {e}")
        sys.exit(1)

    
    print("\nCollected Activities:")
    for activity in visitor.activities:
        print(activity)

if __name__ == '__main__':
    main(sys.argv)
