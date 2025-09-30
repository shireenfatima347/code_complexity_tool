from flask import Flask, render_template, request, jsonify
import ast
import re
import os

app = Flask(__name__)

# ---------------- Python Complexity Analyzer ----------------
class PythonComplexityAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.loop_stack = []
        self.max_depth = 0

    def visit_For(self, node):
        self.loop_stack.append("for")
        self.max_depth = max(self.max_depth, len(self.loop_stack))
        self.generic_visit(node)
        self.loop_stack.pop()

    def visit_While(self, node):
        self.loop_stack.append("while")
        self.max_depth = max(self.max_depth, len(self.loop_stack))
        self.generic_visit(node)
        self.loop_stack.pop()

def analyze_python(code):
    try:
        tree = ast.parse(code)
        analyzer = PythonComplexityAnalyzer()
        analyzer.visit(tree)
        depth = analyzer.max_depth
        if depth == 0:
            time_complexity = "O(1)"
        elif depth == 1:
            time_complexity = "O(n)"
        else:
            time_complexity = f"O(n^{depth})"
        space_complexity = "O(n)"  # simple assumption
        return time_complexity, space_complexity, []
    except SyntaxError as e:
        return None, None, [str(e)]

# ---------------- C/C++ Complexity Analyzer ----------------
def analyze_c_cpp(code):
    # Remove comments
    code = re.sub(r"//.*", "", code)
    code = re.sub(r"/\*[\s\S]*?\*/", "", code)

    lines = code.splitlines()
    max_depth = 0
    current_depth = 0
    stack = []

    for line in lines:
        line = line.strip()
        if re.match(r"^(for|while)\s*\(.*\)", line):
            current_depth += 1
            max_depth = max(max_depth, current_depth)
            stack.append("loop")
        elif line == "}":
            if stack and stack[-1] == "loop":
                stack.pop()
                current_depth -= 1
            elif stack:
                stack.pop()

    if max_depth == 0:
        time_complexity = "O(1)"
    elif max_depth == 1:
        time_complexity = "O(n)"
    else:
        time_complexity = f"O(n^{max_depth})"
    space_complexity = "O(n)"
    return time_complexity, space_complexity, []

# ---------------- Flask Routes ----------------
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    code = data.get("code", "")
    language = data.get("language", "").lower()

    if language == "python":
        time_c, space_c, errors = analyze_python(code)
    elif language in ("c", "cpp", "c++"):
        time_c, space_c, errors = analyze_c_cpp(code)
    else:
        time_c, space_c, errors = None, None, [f"Language '{language}' not supported"]

    if errors:
        return jsonify({"time_complexity": "", "space_complexity": "", "errors": errors})

    return jsonify({
        "time_complexity": time_c,
        "space_complexity": space_c,
        "errors": []
    })

# ---------------- Render-ready Run ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Render's port if available
    app.run(host="0.0.0.0", port=port, debug=True)
