
from fastmcp import FastMCP

mcp = FastMCP("Demo 🚀")

@mcp.tool(name="add")  # 显式声明工具名称
def add(a, b) -> float:
    """Add two numbers"""
    return float(a+b)

@mcp.tool(name='minus')
def minus(a,b) -> float:
    return float(a-b)
@mcp.tool(name='multiply')
def minus(a,b) -> float:
    return float(a*b)
@mcp.tool(name='division')
def minus(a,b):
    try:
        result = a / b
        return float(result)
    except Exception as e:
        print('error:',str(e))
        return None


if __name__ == "__main__":
    mcp.run(
        transport="sse",
        host="0.0.0.0",
        port=3000,
        log_level="debug",
        #allow_origins=["*"]  # 允许跨域访问
    )
