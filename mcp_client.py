import asyncio
from fastmcp import Client


async def main(input_string):
        async with Client("http://localhost:3000/sse") as client:
            if '+' in input_string:
                try:
                    input_num = input_string.replace(' ','').split('+')
                    result = await client.call_tool(
                        "add",  # 必须与服务端工具名一致
                        {"a": float(input_num[0]), "b": float(input_num[1])}
                    )
                except Exception as e:
                    print('error:',str(e))
                    result = None
            elif '-' in input_string:
                try:
                    input_num = input_string.replace(' ', '').split('-')
                    result = await  client.call_tool('minus',{'a':float(input_num[0]),'b':float(input_num[1])})
                except Exception as e:
                    print('error:',str(e))
                    result = None
            elif '*' in input_string:
                try:
                    input_num = input_string.replace(' ', '').split('*')
                    result = await  client.call_tool('multiply',{'a':float(input_num[0]),'b':float(input_num[1])})
                except Exception as e:
                    print('error:',str(e))
                    result = None
            elif '/' in input_string:
                try:
                    input_num = input_string.replace(' ', '').split('/')
                    result = await  client.call_tool('division',{'a':float(input_num[0]),'b':float(input_num[1])})
                except Exception as e:
                    print('error:',str(e))
                    result = None
            if len(result) != 0:
                print(f"计算结果: {result[0].text}")  # 解析字典结果
            else:
                print('计算式错误。')


if __name__ == "__main__":
    while True:
        query = input('Input calculation formula. Input "q" to exit.\nFormula:')
        if query.lower() == 'q':
            break
        asyncio.run(main(query))
