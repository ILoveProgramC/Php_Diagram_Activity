lexer grammar PhpLexer;

PHPStart      : '<?php';
PHPEnd        : '?>';

FUNCTION      : 'function';
IF            : 'if';
ELSE          : 'else';
ELSEIF        : 'elseif';
WHILE         : 'while';
DO            : 'do';
FOR           : 'for';
FOREACH       : 'foreach';
AS            : 'as';
SWITCH        : 'switch';
CASE          : 'case';
DEFAULT       : 'default';
BREAK         : 'break';
CONTINUE      : 'continue';
RETURN        : 'return';
ECHO          : 'echo';
UNSET         : 'unset';
TRY           : 'try';
CATCH         : 'catch';
FINALLY       : 'finally';
THROW         : 'throw';
GOTO          : 'goto';
DECLARE       : 'declare';
NAMESPACE     : 'namespace';
USE           : 'use';
CLASS         : 'class';
INTERFACE     : 'interface';
TRAIT         : 'trait';
EXTENDS       : 'extends';
IMPLEMENTS    : 'implements';
ABSTRACT      : 'abstract';
FINAL         : 'final';
ARRAY         : 'array';

// Compound assignment operators – moraju biti prije kraćih operatora
PlusAssign    : '+=';
MinusAssign   : '-=';
MultiplyAssign: '*=';
DivideAssign  : '/=';
ModAssign     : '%=';
DotAssign     : '.=';
Arrow         : '=>';

// Increment / Decrement operators
PlusPlus      : '++';
MinusMinus    : '--';

// Sintaktički operatori – duži prije kraćih
StrictEqual   : '===';
StrictNotEqual: '!==' ;
Equal         : '==';
NotEqual      : '!=';
LessEqual     : '<=';
GreaterEqual  : '>=';
Less          : '<';
Greater       : '>';
And           : '&&';
Or            : '||';
Not           : '!' ;

// Aritmetički operatori
Plus          : '+';
Minus         : '-';
Multiply      : '*';
Divide        : '/';
Mod           : '%';

// Jednostavni operatori
Assign        : '=';

// Interpunkcija
SemiColon     : ';';
Comma         : ',';
Dot           : '.';
Colon         : ':';
Question      : '?';
OpenParen     : '(';
CloseParen    : ')';
OpenCurly     : '{';
CloseCurly    : '}';
OpenSquare    : '[';
CloseSquare   : ']';
Backslash     : '\\';

// Literali
NULL          : 'null';
Number        : [0-9]+ ('.' [0-9]+)?;
StringLiteral 
    : '"' ( ~["\\] | '\\' . )* '"' 
    | '\'' ( ~["\\] | '\\' . )* '\'';

// Varijable (počinju sa $)
Variable      : '$' [a-zA-Z_][a-zA-Z0-9_]* ;

// Identifikatori (bez dolara)
Identifier    : [a-zA-Z_][a-zA-Z0-9_]* ;

// Dodano za "#" komentare
HashComment   : '#' ~[\r\n]* -> skip;

// Whitespace i komentari (ostali)
WhiteSpace    : [ \t\r\n]+ -> skip;
LineComment   : '//' ~[\r\n]* -> skip;
BlockComment  : '/*' .*? '*/' -> skip;
