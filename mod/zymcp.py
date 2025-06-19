# _*_coding:utf-8 _*_

import traceback
import logging
import asyncio
import json
import time

# from mcp import ClientSession, StdioServerParameters
# from mcp.client.stdio import stdio_client
# from mcp.client.sse import sse_client
# from mcp.client.streamable_http import streamablehttp_client
from fastmcp import Client



'''mcp 客户端连接mcp server运行模块'''


'''日志'''

logger = logging.getLogger(__name__)



# '''mcp获取初始化并执行'''
#
# async def mcp_run(session, cmd, tooldata={}):
#     tool_info = {"content": "", "role": "tool", "tool_call_id": tooldata.get("id", "")}  # 工具调用结果格式
#     try:
#         # 初始化会话
#         logger.warning("初始化连接...")
#         await session.initialize()
#         if cmd in ['call_tool']:
#             logger.warning("调用mcp工具Calling tool...")
#             function = tooldata.get('function', {})
#             tool_name = function.get('name', '').split('/')[0]
#             result = await session.call_tool(tool_name, arguments=json.loads(function.get('arguments')))
#             logger.warning(f"result_all={result}\n\n\n")
#             logger.warning(f"result={result.content}\n\n\n")
#             tool_info["content"] = str(result.content)
#             return tool_info
#         elif cmd in ['list_tool']:
#             logger.warning("获取工具列表...")
#             tools = await session.list_tools()
#             logger.warning(f"可用工具: {[tool.name for tool in tools.tools]}")
#             # print('转为列表')
#             toolslist = [{"type": "function", "function": {"name": t.name, "description": t.description,
#                                                            "parameters": t.inputSchema}} for t in
#                          tools.tools]
#             return toolslist
#         else:
#             logger.warning(f"未知的mcp运行={cmd}")
#             return ''
#     except Exception as e:
#         print(f"mcp执行错误:{e}")
#         print(traceback.format_exc())
#         return tool_info
#
#
# '''mcp_client连接与运行'''
#
# async def mcp_client(mcp_data, cmd, tooldata={}):
#     try:
#         logger.warning(f"开始执行mcp_client, mcp_data={mcp_data}, cmd={cmd}, tooldata={tooldata}")
#         tool_name = tooldata.get('function', {}).get('name', '')
#         mcp_type = mcp_data.get('mcp_type', 'http')
#         mcpServers = mcp_data.get('mcpServers', {})
#         mcpdata2 =mcpServers.get(mcp_data.get('name'), {})
#         if mcp_type in ['http', 'streamablehttp']:  # http方式的mcp
#             logger.warning(f"开始用streamable执行mcp：{mcp_type}, name={tool_name}")
#             url = mcpdata2.get('url', '')
#             async with streamablehttp_client(url) as (read_stream, write_stream, _,):
#                 print("连接成功")
#                 # print(f'read_stream: {read_stream}, write_stream: {write_stream}')
#                 # Create a session using the client streams
#                 async with ClientSession(read_stream, write_stream) as session:
#                     return await mcp_run(session, cmd, tooldata)
#
#         elif mcp_type in ['sse']:
#             logger.warning(f"开始用sse执行mcp：{mcp_type}, name={tool_name}")
#             url = mcpdata2.get('url', '')
#             async with sse_client(url) as (read, write):
#                 print("连接成功")
#                 async with ClientSession(read, write) as session:
#                     return await mcp_run(session, cmd, tooldata)
#
#         elif mcp_type in ['stdio']:
#             logger.warning(f"开始执行mcp：{mcp_type}, name={tool_name}")
#             return []
#
#         else:
#             logger.warning(f"未知的mcp类型:{mcp_type}")
#             return []
#     except Exception as e:
#         logger.error(f'mcprun错误信息：{e}')
#         logger.error(traceback.format_exc())
#         return []


'''mcp_client连接与运行fastmcp'''

async def mcp_client(mcp_data, cmd, tooldata={}):
    try:
        logger.warning(f"开始执行mcp_client, mcp_data={mcp_data}, cmd={cmd}, tooldata={tooldata}")
        tool_info = {"content": "", "role": "tool", "tool_call_id": tooldata.get("id", "")}  # 工具调用结果格式
        tool_name = tooldata.get('function', {}).get('name', '')
        client = Client(mcp_data)
        async with client:
            logger.warning(f"{tool_name}-Client connected: {client.is_connected()}")
            if cmd in ['call_tool']:
                logger.warning("调用mcp工具Calling tool...")
                function = tooldata.get('function', {})
                tool_name = function.get('name', '').split('/')[0]
                result = await client.call_tool(tool_name, arguments=json.loads(function.get('arguments')))
                logger.warning(f"result_all={result}\n\n\n")
                logger.warning(f"result={result}\n\n\n")
                tool_info["content"] = str(result)
                return tool_info
            elif cmd in ['list_tool']:
                logger.warning("获取工具列表...")
                tools = await client.list_tools()
                logger.warning(f"可用工具: {[tool.name for tool in tools]}")
                # print('转为列表')
                toolslist = [{"type": "function", "function": {"name": t.name, "description": t.description,
                                                               "parameters": t.inputSchema}} for t in tools]
                return toolslist
            else:
                logger.warning(f"未知的mcp运行={cmd}")
                return ''

        # Connection is closed automatically here
        logger.warning(f"Client connected: {client.is_connected()}")

    except Exception as e:
        logger.error(f'mcprun错误信息：{e}')
        logger.error(traceback.format_exc())
        return []


'''
运行示例：

工具列表：
[{'type': 'function', 'function': {'name': 'map_geocode', 'description': '地理编码服务: 将地址解析为对应的位置坐标.地址结构越完整, 地址内容越准确, 解析的坐标精度越高.', 'parameters': {'type': 'object', 'required': ['address'], 'properties': {'address': {'type': 'string', 'description': '待解析的地址.最多支持84个字节.可以输入两种样式的值, 分别是：\n1、标准的结构化地址信息, 如北京市海淀区上地十街十号\n2、支持*路与*路交叉口描述方式, 如北一环路和阜阳路的交叉路口\n第二种方式并不总是有返回结果, 只有当地址库中存在该地址描述时才有返回'}}}}}, {'type': 'function', 'function': {'name': 'map_reverse_geocode', 'description': '逆地理编码服务: 根据纬经度坐标, 获取对应位置的地址描述, 所在行政区划, 道路以及相关POI等信息', 'parameters': {'type': 'object', 'required': ['latitude', 'longitude'], 'properties': {'latitude': {'type': 'number', 'description': '纬度 (gcj02ll)'}, 'longitude': {'type': 'number', 'description': '经度 (gcj02ll)'}}}}}, {'type': 'function', 'function': {'name': 'map_search_places', 'description': '地点检索服务: 支持检索城市内的地点信息(最小到city级别), 也可支持圆形区域内的周边地点信息检索.\n城市内检索: 检索某一城市内（目前最细到城市级别）的地点信息.\n周边检索: 设置圆心和半径, 检索圆形区域内的地点信息（常用于周边检索场景）.', 'parameters': {'type': 'object', 'required': ['query'], 'properties': {'query': {'type': 'string', 'description': "检索关键字, 可直接使用名称或类型, 如'天安门', 且可以至多10个关键字, 用英文逗号隔开"}, 'tag': {'type': 'string', 'description': "检索分类, 以中文字符输入, 如'美食', 多个分类用英文逗号隔开, 如'美食,购物'"}, 'region': {'type': 'string', 'description': "检索的行政区划, 可为行政区划名或citycode, 格式为'cityname'或'citycode'"}, 'location': {'type': 'string', 'description': '圆形区域检索的中心点纬经度坐标, 格式为lat,lng'}, 'radius': {'type': 'integer', 'description': '圆形区域检索半径, 单位：米'}}}}}, {'type': 'function', 'function': {'name': 'map_place_details', 'description': '地点详情检索服务: 地点详情检索针对指定POI, 检索其相关的详情信息.\n通过地点检索服务获取POI uid.使用地点详情检索功能, 传入uid, 即可检索POI详情信息, 如评分、营业时间等(不同类型POI对应不同类别详情数据).', 'parameters': {'type': 'object', 'required': ['uid'], 'properties': {'uid': {'type': 'string', 'description': 'POI的唯一标识'}}}}}, {'type': 'function', 'function': {'name': 'map_distance_matrix', 'description': '批量算路服务: 根据起点和终点坐标计算路线规划距离和行驶时间.\n批量算路目前支持驾车、骑行、步行.\n步行时任意起终点之间的距离不得超过200KM, 超过此限制会返回参数错误.\n驾车批量算路一次最多计算100条路线, 起终点个数之积不能超过100.', 'parameters': {'type': 'object', 'required': ['origins', 'destinations'], 'properties': {'origins': {'type': 'string', 'description': '多个起点纬经度坐标, 纬度在前, 经度在后, 多个起点用|分隔'}, 'destinations': {'type': 'string', 'description': '多个终点纬经度坐标, 纬度在前, 经度在后, 多个终点用|分隔'}, 'model': {'type': 'string', 'description': '批量算路类型(driving, riding, walking)'}}}}}, {'type': 'function', 'function': {'name': 'map_directions', 'description': '路线规划服务: 根据起终点`位置名称`或`纬经度坐标`规划出行路线.\n驾车路线规划: 根据起终点`位置名称`或`纬经度坐标`规划驾车出行路线.\n骑行路线规划: 根据起终点`位置名称`或`纬经度坐标`规划骑行出行路线.\n步行路线规划: 根据起终点`位置名称`或`纬经度坐标`规划步行出行路线.\n公交路线规划: 根据起终点`位置名称`或`纬经度坐标`规划公共交通出行路线.', 'parameters': {'type': 'object', 'required': ['origin', 'destination'], 'properties': {'model': {'type': 'string', 'description': '路线规划类型(driving, riding, walking, transit)'}, 'origin': {'type': 'string', 'description': '起点位置名称或纬经度坐标, 纬度在前, 经度在后'}, 'destination': {'type': 'string', 'description': '终点位置名称或纬经度坐标, 纬度在前, 经度在后'}}}}}, {'type': 'function', 'function': {'name': 'map_weather', 'description': '天气查询服务: 通过行政区划或是经纬度坐标查询实时天气信息及未来5天天气预报(注意: 使用经纬度坐标需要高级权限).', 'parameters': {'type': 'object', 'required': [], 'properties': {'location': {'type': 'string', 'description': '经纬度, 经度在前纬度在后, 逗号分隔 (需要高级权限)'}, 'district_id': {'type': 'integer', 'description': '行政区划代码, 需保证为6位无符号整数'}}}}}, {'type': 'function', 'function': {'name': 'map_ip_location', 'description': 'IP定位服务: 根据用户请求的IP获取当前的位置, 当需要知道用户当前位置、所在城市时可以调用该工具获取.', 'parameters': {'type': 'object', 'required': [], 'properties': {'ip': {'type': 'string', 'description': '用户请求的IP地址'}}}}}, {'type': 'function', 'function': {'name': 'map_road_traffic', 'description': '实时路况查询服务: 查询实时交通拥堵情况, 可通过指定道路名和区域形状(矩形, 多边形, 圆形)进行实时路况查询.\n道路实时路况查询: 查询具体道路的实时拥堵评价和拥堵路段、拥堵距离、拥堵趋势等信息.\n矩形区域实时路况查询: 查询指定矩形地理范围的实时拥堵情况和各拥堵路段信息.\n多边形区域实时路况查询: 查询指定多边形地理范围的实时拥堵情况和各拥堵路段信息.\n圆形区域(周边)实时路况查询: 查询某中心点周边半径范围内的实时拥堵情况和各拥堵路段信息.', 'parameters': {'type': 'object', 'required': ['model'], 'properties': {'model': {'type': 'string', 'description': '路况查询类型(road, bound, polygon, around)'}, 'road_name': {'type': 'string', 'description': '道路名称和道路方向, model=road时必传 (如:朝阳路南向北)'}, 'city': {'type': 'string', 'description': '城市名称或城市adcode, model=road时必传 (如:北京市)'}, 'bounds': {'type': 'string', 'description': '区域左下角和右上角的纬经度坐标, 纬度在前, 经度在后, model=bound时必传'}, 'vertexes': {'type': 'string', 'description': '多边形区域的顶点纬经度坐标, 纬度在前, 经度在后, model=polygon时必传'}, 'center': {'type': 'string', 'description': '圆形区域的中心点纬经度坐标, 纬度在前, 经度在后, model=around时必传'}, 'radius': {'type': 'integer', 'description': '圆形区域的半径(米), 取值[1,1000], model=around时必传'}}}}}, {'type': 'function', 'function': {'name': 'map_mark', 'description': '根据旅游规划生成地图规划展示, 当根据用户的需求申城完旅游规划后, 在给用户详细讲解旅游规划的同时, 也需要使用该工具生成旅游规划地图. 该工具只会生成一个分享用的url, 并对针对该url生成一个二维码便于用户分享.', 'parameters': {'type': 'object', 'required': ['text_content'], 'properties': {'text_content': {'type': 'string', 'description': '旅行规划的文本描述(注意避免传入特殊字符, 如\\等)'}}}}}]


调用工具结果：
result=meta=None content=[TextContent(type='text', text='{"status":0,"result":{"location":{"country":"中国","province":"河南省","city":"周口市","name":"川汇","id":"411602"},"now":{"text":"晴","temp":33,"feels_like":34,"rh":37,"wind_class":"2级","wind_dir":"西风","uptime":"20250516145500"},"forecasts":[{"text_day":"多云","text_night":"阴","high":34,"low":22,"wc_day":"<3级","wd_day":"西南风","wc_night":"3~4级","wd_night":"南风","date":"2025-05-16","week":"星期五"},{"text_day":"阴","text_night":"阴","high":32,"low":16,"wc_day":"4~5级","wd_day":"东北风","wc_night":"<3级","wd_night":"东风","date":"2025-05-17","week":"星期六"},{"text_day":"阴","text_night":"晴","high":32,"low":22,"wc_day":"<3级","wd_day":"南风","wc_night":"<3级","wd_night":"南风","date":"2025-05-18","week":"星期日"},{"text_day":"晴","text_night":"晴","high":39,"low":24,"wc_day":"3~4级","wd_day":"西南风","wc_night":"3~4级","wd_night":"西南风","date":"2025-05-19","week":"星期一"},{"text_day":"晴","text_night":"晴","high":39,"low":25,"wc_day":"<3级","wd_day":"南风","wc_night":"<3级","wd_night":"南风","date":"2025-05-20","week":"星期二"}]},"message":"success"}', annotations=None)] isError=False

'''






