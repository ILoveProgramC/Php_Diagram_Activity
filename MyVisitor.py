import re
from antlr4 import *

if "." in __name__:
    from .PhpParser import PhpParser
else:
    from PhpParser import PhpParser
from PhpParserVisitor import PhpParserVisitor

class MyVisitor(PhpParserVisitor):
    def __init__(self):
        self.activities             = []      # top-level aktivnosti
        self.activity_stack         = []      # stek za blok-aktivnosti
        self.functionDeclarations   = {}      # funcName -> blockStatementContext
        self.calledFunctions        = set()
        self.symbolTable            = {}      # varName -> tip
        self.functionParams         = {}      # funcName -> broj parametara
        self.functionParamNames     = {}      # funcName -> [param1, param2, ...]

    def semantic_error(self, message):
        print(f"[SEMANTIC ERROR] {message}")
        raise Exception("Semantička analiza prekinuta zbog greške.")

    def add_activity(self, activity):
        if self.activity_stack:
            self.activity_stack[-1]["children"].append(activity)
        else:
            self.activities.append(activity)


    def visitPhpBlock(self, ctx: PhpParser.PhpBlockContext):
        return self.visitChildren(ctx)

    def visitFunctionDeclaration(self, ctx: PhpParser.FunctionDeclarationContext):
        funcName = ctx.id_().getText() if ctx.id_() else None
        if not funcName:
            return None

      
        self.functionDeclarations[funcName] = ctx.blockStatement()
        names = []
        if ctx.parameterList():
            for p in ctx.parameterList().parameter():
                m = re.search(r'\$(\w+)', p.getText())
                if m:
                    names.append(m.group(1))

        self.functionParamNames[funcName] = names
        self.functionParams[funcName]     = len(names)
        return None
        

    def visitStatement(self, ctx: PhpParser.StatementContext):
        text = ctx.getText().strip().lower()
        if text.startswith("break"):
            self.add_activity({ "type": "break",    "code": "break;"    })
            return None
        if text.startswith("continue"):
            self.add_activity({ "type": "continue", "code": "continue;" })
            return None
        return self.visitChildren(ctx)

    def visitExpressionStatement(self, ctx: PhpParser.ExpressionStatementContext):
        text = ctx.getText().strip()

        # 1) dijeljenje s nulom
        if re.search(r'/\s*0(\.0+)?([^\d]|$)', text):
            self.semantic_error(f"Dijeljenje s nulom u izrazu: '{text}'")

       
        m = re.match(r'^\$(\w+)\s*=\s*(.+);$', text)
        if m:
            varName, value = m.group(1), m.group(2)
            if value.startswith(('"', "'")):
                t = 'string'
            elif re.match(r'^[\d\.]+$', value):
                t = 'number'
            elif value.startswith(('array(', '[')):
                t = 'array'
            else:
                t = 'unknown'
            self.symbolTable[varName] = t
            print(f"[INFO] Detektovana varijabla ${varName} tipa {t}")

       
        for name, declCtx in self.functionDeclarations.items():
            pat   = re.compile(rf'{name}\s*\((.*?)\)\s*;?$')
            match = pat.search(text)
            if not match:
                continue

            args    = match.group(1).strip()
            numArgs = len(args.split(',')) if args else 0
            expArgs = self.functionParams.get(name, -1)

            if expArgs != -1 and numArgs != expArgs:
                print(
                    f"[SEMANTIC WARNING] "
                    f"Poziv funkcije '{name}' sa {numArgs} argumenata "
                    f"(očekivano: {expArgs})"
                )

            prev_stack = self.activity_stack.copy()
            call_act   = {
                "type": "call",
                "code": f"{name}({args})",
                "children": []
            }
            self.add_activity(call_act)
            self.activity_stack.append(call_act)
            self.calledFunctions.add(name)

          
            old_symbols = self.symbolTable.copy()
            for param in self.functionParamNames.get(name, []):
                self.symbolTable[param] = 'unknown'

           
            self.visit(declCtx)

            
            self.symbolTable    = old_symbols
            self.activity_stack = prev_stack
            return None

       
        for w in re.findall(r'(\w+)\s*\(', text):
            if w not in self.functionDeclarations and w not in ['echo','array','isset']:
                self.semantic_error(f"Funkcija '{w}()' nije deklarisana.")

       
        for v in re.findall(r'\$(\w+)', text):
            if v not in self.symbolTable and '=' not in text:
                self.semantic_error(
                    f"Varijabla ${v} korišćena bez deklaracije u '{text}'"
                )

      
        self.add_activity({ "type": "stmt", "code": text })
        return self.visitChildren(ctx)

    def visitIfStatement(self, ctx: PhpParser.IfStatementContext):
        block = { "type": "if", "code": ctx.getText(), "children": [] }
        self.add_activity(block)
        self.activity_stack.append(block)

       
        cond_match = re.search(r'if\s*\((.*?)\)', ctx.getText(), re.DOTALL)
        if cond_match:
            self.check_vars_in_expr(cond_match.group(1))

        
        for substmt in ctx.statement():
            try:
                stmts = substmt.blockStatement().statement()
            except AttributeError:
                stmts = [substmt]

            for stmt in stmts:
                self.visit(stmt)
               
                if block["children"] and block["children"][-1]["type"] == "break":
                    break

        self.activity_stack.pop()
        return None


    def visitWhileStatement(self, ctx: PhpParser.WhileStatementContext):
        block = { "type": "while", "code": ctx.getText(), "children": [] }
        self.add_activity(block)
        self.activity_stack.append(block)

        cond = re.search(r'while\s*\((.*?)\)', ctx.getText(), re.DOTALL).group(1)
        self.check_vars_in_expr(cond)

        self.visitChildren(ctx)
        self.activity_stack.pop()
        return None

    def visitForStatement(self, ctx: PhpParser.ForStatementContext):
        block = { "type": "for", "code": ctx.getText(), "children": [] }
        self.add_activity(block)
        self.activity_stack.append(block)

       
        init, cond, step = re.findall(
            r'for\s*\((.*?);(.*?);(.*?)\)', ctx.getText(), re.DOTALL
        )[0]

      
        m = re.match(r'\s*\$(\w+)\s*=\s*(.+)', init.strip())
        if m:
            varName, value = m.group(1), m.group(2)
            if value.startswith(('"', "'")):
                t = 'string'
            elif re.match(r'^[\d\.]+$', value):
                t = 'number'
            elif value.startswith(('array(', '[')):
                t = 'array'
            else:
                t = 'unknown'
            self.symbolTable[varName] = t
            print(f"[INFO] For-petlja deklarirala varijablu ${varName} tipa {t}")

        
        self.check_vars_in_expr(cond)
        self.check_vars_in_expr(step)

      
        body_stmt = ctx.statement()

        try:
            inner_stmts = body_stmt.blockStatement().statement()
        except AttributeError:
            inner_stmts = [body_stmt]

        for stmt in inner_stmts:
            self.visit(stmt)
            if block["children"] and block["children"][-1]["type"] == "break":
                break

        self.activity_stack.pop()
        return None

    def visitForeachStatement(self, ctx: PhpParser.ForeachStatementContext):
        block = { "type": "foreach", "code": ctx.getText(), "children": [] }
        self.add_activity(block)
        self.activity_stack.append(block)

    
        m = re.search(r'foreach\s*\(\s*\$(\w+)\s+as\s+\$(\w+)\s*\)', ctx.getText())
        if m:
            list_var, item_var = m.group(1), m.group(2)
            if list_var not in self.symbolTable:
                self.semantic_error(
                    f"Varijabla ${list_var} korišćena bez deklaracije u foreach"
                )
            self.symbolTable[item_var] = 'unknown'

        self.visitChildren(ctx)
        self.activity_stack.pop()
        return None

    def visitDoWhileStatement(self, ctx: PhpParser.DoWhileStatementContext):
        block = { "type": "do-while", "code": ctx.getText(), "children": [] }
        self.add_activity(block)
        self.activity_stack.append(block)

        cond = re.search(r'do.*?while\s*\((.*?)\)', ctx.getText(), re.DOTALL).group(1)
        self.check_vars_in_expr(cond)

        self.visitChildren(ctx)
        self.activity_stack.pop()
        return None

    def visitSwitchStatement(self, ctx: PhpParser.SwitchStatementContext):
        block = { "type": "switch", "code": ctx.getText(), "children": [] }
        self.add_activity(block)
        self.activity_stack.append(block)

        cond = re.search(r'switch\s*\((.*?)\)', ctx.getText(), re.DOTALL).group(1)
        self.check_vars_in_expr(cond)

        self.visitChildren(ctx)
        self.activity_stack.pop()
        return None

    def check_vars_in_expr(self, expr_text):
        for v in re.findall(r'\$(\w+)', expr_text):
            if v not in self.symbolTable:
                self.semantic_error(
                    f"Varijabla ${v} korišćena bez prethodne deklaracije u '{expr_text}'"
                )

    def generic_visit(self, ctx):
        if ctx.__class__.__name__ == "FunctionDeclarationContext":
            return None
        return self.visitChildren(ctx)
