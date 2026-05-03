"""
企业级电商知识库演示：品牌与检索参数（可通过环境变量覆盖，便于多环境调试）。
"""
import os

# 业务展示（虚构店铺，仅作演示）
KB_BRAND_NAME = os.getenv("KB_BRAND_NAME", "云栖杂货铺")
KB_SCENE_DESC = os.getenv(
    "KB_SCENE_DESC",
    "售前 / 订单支付 / 配送与退换 / 售后与客诉",
)

# Streamlit 页面
PAGE_TITLE = os.getenv("KB_PAGE_TITLE", "电商知识库问答助手")
PAGE_ICON = os.getenv("KB_PAGE_ICON", "🛒")

# 检索
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "4"))

# 小白友好的一句话描述
KB_SIMPLE_DESC = "你可以问我关于商品、订单、售后的任何问题"
