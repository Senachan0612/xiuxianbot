"""评估"""

import ast
import operator

# 定义支持的操作符
operators = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.BitXor: operator.xor,
    ast.USub: operator.neg,
}


# 评估 算术表达式
def equation_eval(_expr):
    """
        算术表达式
    :param _expr: 算术表达式字符串
    :return: 计算结果
    """

    def _eval(_node):
        if isinstance(_node, ast.Num):  # 数字
            return _node.n
        elif isinstance(_node, ast.BinOp):  # 二元运算符
            return operators[type(_node.op)](_eval(_node.left), _eval(_node.right))
        elif isinstance(_node, ast.UnaryOp):  # 一元运算符
            return operators[type(_node.op)](_eval(_node.operand))
        else:
            raise TypeError(_node)

    _node = ast.parse(_expr, mode='eval').body
    return _eval(_node)


# 评估 可迭代字符串
iter_eval = ast.literal_eval

# 评估
normal_eval = eval
