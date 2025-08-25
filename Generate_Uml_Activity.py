import re

def escape_text(txt):
    return txt.replace('"', '\\"')

def stylize_statement(stmt):
    stmt = stmt.strip()
    upper = {
        "if": "IF", "else": "ELSE", "elseif": "ELSE IF",
        "for": "FOR", "while": "WHILE", "foreach": "FOREACH",
        "do-while": "DO-WHILE", "switch": "SWITCH",
        "break": "BREAK", "continue": "CONTINUE", "case": "CASE"
    }
    for k, v in upper.items():
        pattern = rf'^{k}\b'
        if re.match(pattern, stmt):
            stmt = re.sub(pattern, v, stmt, count=1)
            break
    return escape_text(stmt)

def extract_condition(code, kw):
    m = re.search(rf'{kw}\s*\((.*?)\)', code)
    return m.group(1).strip() if m else ""

def extract_body(code):
    m = re.search(r'\{(.*)\}$', code, re.DOTALL)
    return m.group(1).strip() if m else ""

def contains_type(target_type, node):
    if node["type"].lower() == target_type:
        return True
    for child in node.get("children", []):
        if contains_type(target_type, child):
            return True
    return False

def generate_activity_uml(activities):
    lines = [
        "@startuml",
        "set namespaceSeparator none",
        "skinparam backgroundColor #f9f9f9",
        "skinparam shadowing false",
        "skinparam activity {",
        "  BackgroundColor #dfefff",
        "  BorderColor #3399cc",
        "  FontColor black",
        "  FontSize 14",
        "  FontName Consolas",
        "  FontStyle bold",
        "  Padding 15",                
        "  ArrowThickness 0.8",        
        "  ArrowColor #444444",        
        "  BarColor #3399cc",          
        "}",
        "skinparam note {",
        "  FontSize 13",
        "  BackgroundColor #ffffcc",
        "  BorderColor #cccccc",
        "  Padding 10",
        "  Margin 10",
        "}",
        "skinparam defaultTextAlignment left",   
        "skinparam maxMessageSize 100",          
        "start"
    ]


    def _render(acts, indent):
        pref = "  " * indent

        for act in acts:
            t = act["type"].lower()
            code = act["code"].replace("\n", " ")

            # ---- IF / ELSEIF / ELSE ----
            if t == "if":
                raw = code.replace("else if", "elseif")
                parts = re.findall(
                    r'(if|elseif|else)\s*(?:\((.*?)\))?\s*\{(.*?)}',
                    raw, re.DOTALL
                )

                for idx, (kw, cond, body) in enumerate(parts):
                    label = "true" if kw == "if" else "elseif" if kw == "elseif" else "else"
                    cond_txt = f"{kw.upper()} {cond.strip()}" if cond else "ELSE"

                    if kw == "if":
                        lines.append(f"{pref}if ({cond_txt}) then ({label})")
                    elif kw == "elseif":
                        lines.append(f"{pref}elseif ({cond_txt}) then (true)")
                    else:
                        lines.append(f"{pref}else ({label})")

                    stmts = [s.strip() for s in body.split(";") if s.strip()]
                    for stmt in stmts:
                        low = stmt.lower()
                        if low.startswith("break"):
                            lines.append(f"{pref}  :BREAK;")
                            lines.append(f"{pref}break")
                            break
                        elif low.startswith("continue"):
                            lines.append(f"{pref}  :CONTINUE;")
                            break
                        else:
                            lines.append(f"{pref}  :{stylize_statement(stmt)};")

                lines.append(f"{pref}endif")
                continue


            # ---- SWITCH kao IF/ELSEIF/ELSE ----
            elif t == "switch":
                expr = extract_condition(code, "switch")
                body = extract_body(code)
                pattern = re.compile(
                    r'case\s*(.+?)\s*:(.*?)(?=case\s*.+?:|default:|\Z)',
                    re.DOTALL
                )
                cases = pattern.findall(body)
                m_def = re.search(r'default\s*:(.*)', body, re.DOTALL)
                default_blk = m_def.group(1).strip() if m_def else ""

                lines.append(f"{pref}:SWITCH ({expr});")

                if cases:
                    val, blk = cases[0]
                    cond = f"{expr} == {val.strip()}"
                    lines.append(f"{pref}if ({cond}) then (case {val.strip()})")
                    for stmt in blk.split(";"):
                        if stmt.strip():
                            lines.append(f"{pref}  :{stylize_statement(stmt)};")
                else:
                    lines.append(f"{pref}if (FALSE) then (no cases)")

                for val, blk in cases[1:]:
                    cond = f"{expr} == {val.strip()}"
                    lines.append(f"{pref}elseif ({cond}) then (case {val.strip()})")
                    for stmt in blk.split(";"):
                        if stmt.strip():
                            lines.append(f"{pref}  :{stylize_statement(stmt)};")

                lines.append(f"{pref}else (default)")
                for stmt in default_blk.split(";"):
                    if stmt.strip():
                        lines.append(f"{pref}  :{stylize_statement(stmt)};")

                lines.append(f"{pref}endif")
                continue

            # ---- LOOPS ----
            if t in ("while", "for", "foreach", "do-while"):
                cond_kw = "while" if t == "do-while" else t
                cond = extract_condition(code, cond_kw)
                label = f"{t}_loop".replace("-", "_")

                lines.append(f"{pref}label {label}")
                if t == "do-while":
                    lines.append(f"{pref}repeat")
                else:
                    lines.append(f"{pref}while ({t.upper()} {cond}) is (false)")

                if act.get("children"):
                    for c in act["children"]:
                        _render([c], indent + 1)
                        typ = c["type"].lower()
                        if typ == "break":
                            lines.append(f"{pref}break")
                            break
                        elif typ == "continue":
                            break
                else:
                    for stmt in extract_body(code).split(";"):
                        stmt = stmt.strip()
                        if not stmt:
                            continue
                        lines.append(f"{pref}  :{stylize_statement(stmt)};")

                if t == "do-while":
                    lines.append(f"{pref}repeat while (DO-WHILE {cond})")
                else:
                    lines.append(f"{pref}endwhile (true)")
                lines.append(f"{pref}:izlaz iz {t}-petlje;")
                continue

            # ---- CALL ----
            elif t == "call":
                lines.append(f"{pref}:Poziv funkcije {stylize_statement(code)};")
                _render(act.get("children", []), indent + 1)
                fn = code.split("(")[0]
                lines.append(f"{pref}:IZLAZ IZ FUNKCIJE {fn};")

            # ---- DEFAULT ----
            else:
                lines.append(f"{pref}:{stylize_statement(code)};")

    _render(activities, 0)
    lines.append("""legend
    IF BLOK -> True ili False grana
    ELSE IF BLOK -> True ili False grana
    ELSE BLOK -> False grana
    BREAK/CONTINUE -> Naredbe prekida petlje/preskok iteracije
    FOR petlja -> inicijalizacija; uslov; inkrement ==> tijelo petlje
    WHILE petlja -> uslov ==> tijelo petlje
    DO WHILE petlja -> tijelo petlje ==> uslov
    SWITCH blok -> caseovi ==> default (false)
    end legend""")
    lines.append("stop")
    lines.append("@enduml")
    return "\n".join(lines)
