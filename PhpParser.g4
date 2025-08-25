parser grammar PhpParser;

options { tokenVocab=PhpLexer; }

id : Identifier ;

phpBlock
    : PHPStart topStatement* PHPEnd EOF
    ;

topStatement
    : namespaceDeclaration
    | useDeclaration
    | innerStatement
    ;

innerStatementList
    : innerStatement*
    ;

innerStatement
    : statement
    | functionDeclaration
    | classDeclaration
    | interfaceDeclaration
    | traitDeclaration
    ;

namespaceDeclaration
    : NAMESPACE qualifiedName SemiColon
    ;

useDeclaration
    : USE qualifiedName (Comma qualifiedName)* SemiColon
    ;

qualifiedName
    : id (Backslash id)*
    ;

statement
    : blockStatement
    | ifStatement
    | whileStatement
    | doWhileStatement
    | forStatement
    | foreachStatement
    | switchStatement
    | breakStatement
    | continueStatement
    | returnStatement
    | echoStatement
    | expressionStatement
    | unsetStatement
    | tryCatchFinally
    | throwStatement
    | gotoStatement
    | declareStatement
    | emptyStatement
    ;

blockStatement
    : OpenCurly innerStatementList CloseCurly
    ;

ifStatement
    : IF OpenParen expression CloseParen statement 
      (ELSEIF OpenParen expression CloseParen statement)* 
      (ELSE statement)?
    ;

whileStatement
    : WHILE OpenParen expression CloseParen statement
    ;

doWhileStatement
    : DO statement WHILE OpenParen expression CloseParen SemiColon
    ;

forStatement
    : FOR OpenParen forInit? SemiColon expression? SemiColon forUpdate? CloseParen statement
    ;

forInit 
    : expressionList
    ;

forUpdate 
    : expressionList
    ;

foreachStatement
    : FOREACH OpenParen expression AS expression (Comma expression)? CloseParen statement
    ;

switchStatement
    : SWITCH OpenParen expression CloseParen OpenCurly switchBlock* CloseCurly
    ;

switchBlock
    : (CASE expression Colon | DEFAULT Colon) innerStatementList
    ;

breakStatement
    : BREAK expression? SemiColon
    ;

continueStatement
    : CONTINUE expression? SemiColon
    ;

returnStatement
    : RETURN expression? SemiColon
    ;

echoStatement
    : ECHO expressionList SemiColon
    ;

expressionStatement
    : expression SemiColon
    ;

unsetStatement
    : UNSET OpenParen expressionList CloseParen SemiColon
    ;

tryCatchFinally
    : TRY blockStatement (catchClause+ (finallyClause)? | finallyClause)
    ;

catchClause
    : CATCH OpenParen expression CloseParen blockStatement
    ;

finallyClause
    : FINALLY blockStatement
    ;

throwStatement
    : THROW expression SemiColon
    ;

gotoStatement
    : GOTO id SemiColon
    ;

declareStatement
    : DECLARE OpenParen expression CloseParen statement
    ;

emptyStatement
    : SemiColon
    ;

expressionList
    : expression (Comma expression)*
    ;

expression
    : assignmentExpression
    ;

assignmentExpression
    : conditionalExpression ( (Assign | PlusAssign | MinusAssign | MultiplyAssign |
                               DivideAssign | ModAssign | DotAssign)
                            assignmentExpression )?
    ;

conditionalExpression
    : logicalOrExpression (Question expression Colon conditionalExpression)?
    ;

logicalOrExpression
    : logicalAndExpression (Or logicalAndExpression)*
    ;

logicalAndExpression
    : equalityExpression (And equalityExpression)*
    ;

equalityExpression
    : relationalExpression ((Equal | NotEqual | StrictEqual | StrictNotEqual) relationalExpression)*
    ;

// Uređujemo operaciju spajanja (.) – ona ima nižu precedenciju od +/-
concatExpression
    : additiveExpression (Dot additiveExpression)*
    ;

// Sada u relacijskom izrazu koristimo concatExpression kao operand.
relationalExpression
    : concatExpression ((Less | Greater | LessEqual | GreaterEqual) concatExpression)*
    ;

additiveExpression
    : multiplicativeExpression ((Plus | Minus) multiplicativeExpression)*
    ;

multiplicativeExpression
    : unaryExpression ((Multiply | Divide | Mod) unaryExpression)*
    ;

unaryExpression
    : (Plus | Minus | Not) unaryExpression
    | primaryExpression
    ;

primaryExpression
    : ( id (OpenParen expressionList? CloseParen)? | Variable ) (PlusPlus | MinusMinus)?
    | Number
    | StringLiteral
    | NULL
    | arrayLiteral
    | OpenParen expression CloseParen
    ;

arrayLiteral
    : ARRAY OpenParen expressionList? CloseParen
    | OpenSquare expressionList? CloseSquare
    ;



functionDeclaration
    : FUNCTION id OpenParen parameterList? CloseParen blockStatement
    ;

parameterList
    : parameter (Comma parameter)*
    ;

// Pravilo za parametar – default vrijednost sada dopušta samo konstantne izraze (defaultExpr)
parameter
    : (typeSpecifier)? (Variable | id) (Assign defaultExpr)?
    ;

defaultExpr
    : Number
    | StringLiteral
    | NULL
    | arrayLiteral
    ;

typeSpecifier
    : ARRAY
    ;

classDeclaration
    : (ABSTRACT | FINAL)? CLASS id (extendsClause)? (implementsClause)? blockStatement
    ;

extendsClause
    : EXTENDS qualifiedName
    ;

implementsClause
    : IMPLEMENTS qualifiedName (Comma qualifiedName)*
    ;

interfaceDeclaration
    : INTERFACE id (extendsClause)? blockStatement
    ;

traitDeclaration
    : TRAIT id blockStatement
    ;
