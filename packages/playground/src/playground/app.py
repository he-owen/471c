import subprocess
import sys
import tempfile
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from L1.pretty import pretty_program as l1_pretty
from L1.to_python import to_ast_program
from L2.cps_convert import cps_convert_program
from L2.optimize import optimize_program
from L2.pretty import pretty_program as l2_pretty
from L3.check import check_program
from L3.desugar import desugar_program
from L3.eliminate_letrec import eliminate_letrec_program
from L3.parse import parse_program
from L3.pretty import pretty_program as l3_pretty
from L3.uniqify import uniqify_program

STATIC_DIR = Path(__file__).parent.parent.parent / "static"

app = Flask(__name__, static_folder=str(STATIC_DIR))

EXAMPLES = {
    "Addition": {
        "code": "(l3 (m n)\n  (+ m n))",
        "args": [3, 4],
    },
    "Factorial": {
        "code": (
            "(l3 (x)\n"
            "  (letrec\n"
            "    ((fact\n"
            "       (\\ (n)\n"
            "         (if\n"
            "            (== n 0)\n"
            "            1\n"
            "            (* n\n"
            "                (fact (- n 1)))))))\n"
            "    (fact x)))"
        ),
        "args": [5],
    },
    "Fibonacci": {
        "code": (
            "(l3 (n)\n"
            "  (letrec\n"
            "    ((fib\n"
            "      (\\ (n)\n"
            "        (if\n"
            "          (< n 2)\n"
            "          n\n"
            "          (+ (fib (- n 1))\n"
            "             (fib (- n 2)))))))\n"
            "    (fib n)))"
        ),
        "args": [10],
    },
    "Closures": {
        "code": (
            "(l3 (m n)\n"
            "  (let ((make_adder\n"
            "         (\\ (x)\n"
            "           (\\ (y)\n"
            "             (+ x y)))))\n"
            "    (let ((adder (make_adder m)))\n"
            "      (adder n))))"
        ),
        "args": [3, 4],
    },
    "Division & Modulo": {
        "code": "(l3 (n)\n  (+ (/ n 2) (% n 2)))",
        "args": [7],
    },
    "Booleans & Logic": {
        "code": (
            "(l3 (x)\n"
            "  (let ((positive (if (> x 0) #t #f)))\n"
            "    (if (and positive (not #f))\n"
            "      x\n"
            "      0)))"
        ),
        "args": [42],
    },
    "Print": {
        "code": '(l3 ()\n  (begin\n    (print 42)\n    (print "hello world")\n    0))',
        "args": [],
    },
    "Strings": {
        "code": '(l3 ()\n  (let ((greeting (string-append "hello" " world")))\n    (begin\n      (print greeting)\n      (string-length greeting))))',
        "args": [],
    },
}


def compile_program(code: str):
    stages = {}
    error = None

    try:
        l3_parsed = parse_program(code)
        stages["l3_parsed"] = {
            "sexp": l3_pretty(l3_parsed),
            "json": l3_parsed.model_dump(),
        }
    except Exception as e:
        return stages, f"Parse error: {e}", None

    try:
        l3_desugared = desugar_program(l3_parsed)
        stages["l3_desugared"] = {
            "sexp": l3_pretty(l3_desugared),
            "json": l3_desugared.model_dump(),
        }
    except Exception as e:
        return stages, f"Desugar error: {e}", None

    try:
        check_program(l3_desugared)
    except Exception as e:
        return stages, f"Semantic error: {e}", None

    try:
        fresh, l3_uniq = uniqify_program(l3_desugared)
    except Exception as e:
        return stages, f"Uniqify error: {e}", None

    try:
        l2 = eliminate_letrec_program(l3_uniq)
        stages["l2"] = {
            "sexp": l2_pretty(l2),
            "json": l2.model_dump(),
        }
    except Exception as e:
        return stages, f"LetRec elimination error: {e}", None

    try:
        l2_opt = optimize_program(l2)
        stages["l2_optimized"] = {
            "sexp": l2_pretty(l2_opt),
            "json": l2_opt.model_dump(),
        }
    except Exception as e:
        return stages, f"Optimization error: {e}", None

    try:
        l1 = cps_convert_program(l2_opt, fresh)
        stages["l1"] = {
            "sexp": l1_pretty(l1),
            "json": l1.model_dump(),
        }
    except Exception as e:
        return stages, f"CPS conversion error: {e}", None

    try:
        python_code = to_ast_program(l1)
        stages["python"] = python_code
    except Exception as e:
        return stages, f"Code generation error: {e}", None

    return stages, error, python_code


def execute_program(python_code: str, args: list) -> tuple[str, str | None]:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        tmp_path = f.name

    try:
        str_args = [str(a) for a in args]
        result = subprocess.run(
            [sys.executable, tmp_path, *str_args],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return "", f"Runtime error:\n{result.stderr}"
        return result.stdout, None
    except subprocess.TimeoutExpired:
        return "", "Error: program timed out (5 second limit)"
    except Exception as e:
        return "", f"Execution error: {e}"
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@app.route("/")
def index():
    return send_from_directory(str(STATIC_DIR), "index.html")


@app.route("/api/run", methods=["POST"])
def run_program():
    data = request.get_json()
    code = data.get("code", "")
    args = data.get("args", [])

    stages, error, python_code = compile_program(code)

    output = ""
    if error is None and python_code is not None:
        output, exec_error = execute_program(python_code, args)
        if exec_error:
            error = exec_error

    return jsonify({
        "stages": stages,
        "output": output,
        "error": error,
    })


@app.route("/api/examples", methods=["GET"])
def get_examples():
    return jsonify(EXAMPLES)


def main():
    import os

    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", debug=debug, port=port)


if __name__ == "__main__":
    main()
