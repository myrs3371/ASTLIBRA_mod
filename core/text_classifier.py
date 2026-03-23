"""游戏文本自动分类器"""


class TextClassifier:
    """游戏文本自动分类器"""

    CATEGORIES = {
        'dialogue': '对话文本',
        'attribute': '属性/状态',
        'ui': '系统UI',
        'location': '地名/标题',
        'skill': '技能描述',
        'item': '物品描述',
        'other': '其他'
    }

    # 关键词字典
    UI_KEYWORDS = ['确定', '取消', '退出', '保存', '已存档', '合成', '需要', '获得', '选择', '装备', '道具']
    LOCATION_KEYWORDS = ['出口', '入口', '山', '海', '城', '村', '洞窟', '森林', '神殿', '谷', '通往']
    SKILL_KEYWORDS = ['攻击', '防御', '召唤', '魔法', '效果', '伤害', '恢复', '技能', '释放', '施放', '精灵']
    ITEM_KEYWORDS = ['装备', '武器', '盔甲', '药水', '道具', '材料', '宝物', '锤', '剑', '盾', '戒指', '打造']
    ATTRIBUTE_KEYWORDS = ['体力', '精力', '魔导力', '防御力', '攻击力', '幸运', '抗性', '能力', '最大']

    @classmethod
    def classify(cls, text: str) -> str:
        """分类单条文本"""
        if not text or text in ['-', 'None', '']:
            return 'other'

        text = str(text).strip()
        length = len(text)

        # 规则1：对话文本（优先级最高）
        if '@^' in text or '[n_nr]' in text:
            return 'dialogue'

        # 规则2：属性/状态
        if (':' in text and length < 20) or any(mark in text for mark in ['[★]', '[强]', '[极]']):
            return 'attribute'
        if any(keyword in text for keyword in cls.ATTRIBUTE_KEYWORDS) and length < 30:
            return 'attribute'

        # 规则3：系统UI（短文本）
        if length < 15 and any(keyword in text for keyword in cls.UI_KEYWORDS):
            return 'ui'

        # 规则4：地名/标题
        if '■' in text:
            return 'location'
        if any(keyword in text for keyword in cls.LOCATION_KEYWORDS) and length < 30:
            return 'location'

        # 规则5：技能描述
        if 20 <= length <= 100 and any(keyword in text for keyword in cls.SKILL_KEYWORDS):
            return 'skill'

        # 规则6：物品描述
        if any(keyword in text for keyword in cls.ITEM_KEYWORDS):
            return 'item'
        if 10 <= length <= 100 and '。' in text:
            return 'item'

        # 规则7：其他
        return 'other'

    @classmethod
    def get_category_name(cls, category_key: str) -> str:
        """获取分类中文名称"""
        return cls.CATEGORIES.get(category_key, '未知')
