from typing import Any, Dict
import ast
import operator
from app.tools.interfaces.abstract_tool import AbstractTool
from app.tools.models.tool_context import ToolContext

class CalculatorTool(AbstractTool):
    def _evaluate_ast(self, node):
        allowed_operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos
        }
        
        allowed_functions = {
            'abs': abs,
            'round': round,
            'min': min,
            'max': max
        }
        
        if isinstance(node, ast.Num): # < python 3.8
            return node.n
        elif isinstance(node, ast.Constant): # >= python 3.8
            if not isinstance(node.value, (int, float)):
                raise ValueError("Only numeric constants allowed")
            return node.value
        elif isinstance(node, ast.BinOp):
            if type(node.op) not in allowed_operators:
                raise ValueError(f"Operator {type(node.op)} not allowed")
            return allowed_operators[type(node.op)](self._evaluate_ast(node.left), self._evaluate_ast(node.right))
        elif isinstance(node, ast.UnaryOp):
            if type(node.op) not in allowed_operators:
                raise ValueError(f"Operator {type(node.op)} not allowed")
            return allowed_operators[type(node.op)](self._evaluate_ast(node.operand))
        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name) or node.func.id not in allowed_functions:
                raise ValueError("Only abs, round, min, max functions allowed")
            args = [self._evaluate_ast(arg) for arg in node.args]
            return allowed_functions[node.func.id](*args)
        elif isinstance(node, ast.Expression):
            return self._evaluate_ast(node.body)
        else:
            raise ValueError(f"Unsupported AST node: {type(node)}")

    async def execute(self, arguments: Dict[str, Any], context: ToolContext) -> Any:
        expression = arguments.get("expression")
        if not expression:
            raise ValueError("Missing 'expression' argument")
            
        try:
            tree = ast.parse(expression, mode='eval')
            return self._evaluate_ast(tree)
        except Exception as e:
            return f"Error evaluating expression: {str(e)}"
