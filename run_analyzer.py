import sys
import json
from antlr4 import *
from PhpLexer import PhpLexer
from PhpParser import PhpParser
from MyVisitor import MyVisitor
from Generate_Uml_Activity import generate_activity_uml 
from StrictErrorListener import StrictErrorListener
import subprocess
import os

def ensure_output_folder(folder="PlantUML_code"):
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder 

def main(input_file):
    input_stream = FileStream(input_file, encoding='utf-8')


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

   
    uml_code = generate_activity_uml(visitor.activities)

   
    output_dir = ensure_output_folder()
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    uml_file = os.path.join(output_dir, f"{base_name}.uml")

    with open(uml_file, "w", encoding="utf-8") as f:
        f.write(uml_code)
    print(f"PlantUML kod sačuvan u: {uml_file}")

    #
    try:
        plantuml_path = os.path.join(os.path.dirname(__file__), "jars", "plantuml.jar")
        subprocess.run(["java", "-jar", plantuml_path, uml_file], check=True)
        print(f"Dijagram kreiran: {os.path.join(output_dir, base_name)}.png")
    except FileNotFoundError:
        print("PlantUML nije pronađen. Preskačem vizuelno generisanje.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("👉 Upotreba: python run_analyzer.py fajl.php")
        sys.exit(1)
    main(sys.argv[1])
