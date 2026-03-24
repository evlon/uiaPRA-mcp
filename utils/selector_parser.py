"""
Selector 语法解析和转换工具
"""
import re
import ast
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SelectorParser:
    """Selector 语法解析器"""
    
    def __init__(self):
        pass
    
    def parse(self, selector_str: str) -> List[Dict[str, Any]]:
        """
        解析 selector 字符串
        :param selector_str: tdSelector 语法字符串
        :return: 解析后的结构
        
        示例输入:
        "[  { 'wnd' : [ ('Text' , '窗口') , ('App' , 'notepad.exe') ] } ,  
           { 'ctrl' : [ ('AutomationId' , 'MenuBar') ] }]"
        
        示例输出:
        [
          {
            'type': 'wnd',
            'conditions': [
              {'property': 'Text', 'value': '窗口', 'match_type': 'exact'},
              {'property': 'App', 'value': 'notepad.exe', 'match_type': 'exact'}
            ]
          },
          {
            'type': 'ctrl',
            'conditions': [
              {'property': 'AutomationId', 'value': 'MenuBar', 'match_type': 'exact'}
            ]
          }
        ]
        """
        try:
            # 移除外层方括号
            selector_str = selector_str.strip()
            if selector_str.startswith('[') and selector_str.endswith(']'):
                selector_str = selector_str[1:-1]
            
            # 分割节点
            nodes = self._split_nodes(selector_str)
            
            parsed_nodes = []
            for node_str in nodes:
                parsed_node = self._parse_node(node_str.strip())
                if parsed_node:
                    parsed_nodes.append(parsed_node)
            
            return parsed_nodes
            
        except Exception as e:
            logger.error(f"Error parsing selector: {e}")
            raise ValueError(f"Invalid selector syntax: {e}")
    
    def _split_nodes(self, selector_str: str) -> List[str]:
        """分割节点 (处理嵌套括号)"""
        nodes = []
        current = []
        depth = 0
        
        for char in selector_str:
            if char == '{':
                depth += 1
                current.append(char)
            elif char == '}':
                depth -= 1
                current.append(char)
                if depth == 0:
                    nodes.append(''.join(current).strip())
                    current = []
            elif char == ',' and depth == 0:
                if current:
                    nodes.append(''.join(current).strip())
                    current = []
            else:
                current.append(char)
        
        if current:
            nodes.append(''.join(current).strip())
        
        return nodes
    
    def _parse_node(self, node_str: str) -> Optional[Dict[str, Any]]:
        """解析单个节点"""
        try:
            # 使用 ast.literal_eval 安全解析
            node_dict = ast.literal_eval(node_str)
            
            if not isinstance(node_dict, dict):
                return None
            
            result = {'conditions': []}
            
            for key, value in node_dict.items():
                if key in ['wnd', 'ctrl']:
                    result['type'] = key
                    if isinstance(value, list):
                        for condition in value:
                            if isinstance(condition, tuple) and len(condition) >= 2:
                                prop = condition[0]
                                val = condition[1]
                                match_type = 'exact'
                                
                                if len(condition) >= 3:
                                    match_type = self._parse_match_type(condition[2])
                                
                                result['conditions'].append({
                                    'property': prop,
                                    'value': val,
                                    'match_type': match_type
                                })
                    elif isinstance(value, str):
                        result['conditions'].append({
                            'property': 'Text',
                            'value': value,
                            'match_type': 'exact'
                        })
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing node '{node_str}': {e}")
            return None
    
    def _parse_match_type(self, match_str: str) -> str:
        """解析匹配类型"""
        match_str = match_str.lower()
        if 'fuzz' in match_str or 'fuzzy' in match_str:
            return 'fuzzy'
        elif 'regex' in match_str or 're' in match_str:
            return 'regex'
        else:
            return 'exact'
    
    def to_dict(self, selector_str: str) -> dict:
        """转换为字典格式"""
        return {'nodes': self.parse(selector_str)}
    
    def to_simple_selector(self, selector_str: str) -> str:
        """
        转换为简化 selector (只保留关键属性)
        :return: 简化后的 selector 字符串
        """
        parsed = self.parse(selector_str)
        simplified = []
        
        for node in parsed:
            simple_conditions = []
            for cond in node['conditions']:
                if cond['property'] in ['Text', 'AutomationId', 'App']:
                    simple_conditions.append(cond)
            
            if simple_conditions:
                simplified.append({
                    'type': node['type'],
                    'conditions': simple_conditions
                })
        
        return str(simplified)


class SelectorBuilder:
    """Selector 构建器"""
    
    @staticmethod
    def from_properties(node_type: str, properties: Dict[str, Any]) -> str:
        """
        从属性构建 selector
        :param node_type: 'wnd' 或 'ctrl'
        :param properties: 属性字典
        :return: selector 字符串
        
        示例:
        from_properties('wnd', {'Text': '窗口', 'App': 'notepad.exe'})
        返回: "[{'wnd': [('Text', '窗口'), ('App', 'notepad.exe')]}]"
        """
        conditions = []
        for prop, value in properties.items():
            conditions.append((prop, str(value)))
        
        node = {node_type: conditions}
        return f"[{node}]"
    
    @staticmethod
    def from_path(path: List[Dict[str, Any]]) -> str:
        """
        从路径构建 selector
        :param path: 节点列表 [{'type': 'wnd', 'conditions': {...}}, ...]
        :return: selector 字符串
        """
        nodes = []
        for node in path:
            node_type = node.get('type', 'ctrl')
            conditions = []
            
            props = node.get('conditions', {})
            if isinstance(props, dict):
                for prop, value in props.items():
                    conditions.append((prop, str(value)))
            elif isinstance(props, list):
                conditions = props
            
            nodes.append({node_type: conditions})
        
        return str(nodes)
    
    @staticmethod
    def add_fuzzy_match(selector_str: str, properties: List[str] = None) -> str:
        """
        为指定属性添加模糊匹配
        :param selector_str: 原 selector
        :param properties: 要添加模糊匹配的属性列表
        :return: 修改后的 selector
        """
        if properties is None:
            properties = ['Text']
        
        parser = SelectorParser()
        parsed = parser.parse(selector_str)
        
        for node in parsed:
            for cond in node['conditions']:
                if cond['property'] in properties:
                    cond['match_type'] = 'fuzzy'
        
        # 重建 selector (简化处理)
        return str(parsed)


def natural_to_selector(description: str) -> str:
    """
    将自然语言描述转换为 selector (简单规则匹配)
    :param description: 如 "notepad 的保存按钮"
    :return: selector 字符串
    """
    # 简单规则匹配
    patterns = [
        (r'(.*)的 (.*) 按钮', lambda m: [
            {'type': 'wnd', 'conditions': {'Text': m.group(1)}},
            {'type': 'ctrl', 'conditions': {'Text': m.group(2), 'ControlType': 'Button'}}
        ]),
        (r'(.*)窗口', lambda m: [
            {'type': 'wnd', 'conditions': {'Text': m.group(1)}}
        ]),
        (r'(.*)菜单', lambda m: [
            {'type': 'ctrl', 'conditions': {'Text': m.group(1), 'ControlType': 'MenuItem'}}
        ]),
    ]
    
    for pattern, builder in patterns:
        match = re.match(pattern, description)
        if match:
            path = builder(match)
            return SelectorBuilder.from_path(path)
    
    # 默认：作为窗口标题
    return SelectorBuilder.from_properties(
        'wnd', 
        {'Text': description}
    )
