from typing import List, Set


def greedy_text_splitter(
    text: str, max_length: int, punctuation: Set[str] = set()
) -> List[str]:
    """
    使用贪婪算法进行文本分割。

    优先在标点符号处分割，确保每个分段不超过`max_length`。
    如果在`max_length`的窗口内找不到标点，则进行硬分割。

    Args:
        text (str): 需要分割的原始文本。
        max_length (int): 每个分段的最大长度（字符数）。
        punctuation (Set[str], optional):
            用于分割的标点符号集合。如果为 None，则使用默认的中英文标点。

    Returns:
        List[str]: 分割后的文本段落列表。
    """
    if not punctuation:
        # 默认使用常见的中英文标点
        punctuation = {"。", "！", "？", "……", "；", "，", ".", "!", "?", ";", ","}

    if not text:
        return []

    # 先去除文本首尾的空白字符
    text = text.strip()

    if len(text) <= max_length:
        # 对于短文本，移除末尾的标点符号
        if text and text[-1] in punctuation:
            return [text[:-1].strip()]
        return [text]

    segments = []
    current_pos = 0

    while current_pos < len(text):
        # 确定下一次搜索的窗口末尾位置
        # min()确保我们不会超出文本的总长度
        end_pos = min(current_pos + max_length, len(text))

        # 如果剩余文本不再需要分割，直接添加并结束
        if end_pos == len(text):
            segment = text[current_pos:]
            # 移除末尾的标点符号
            if segment and segment[-1] in punctuation:
                segment = segment[:-1]
            segments.append(segment.strip())
            break

        split_pos = -1
        split_char_pos = -1

        # 贪婪策略：从窗口末尾向前搜索最后一个标点符号
        # range(end_pos, current_pos, -1) 表示从 end_pos-1 到 current_pos
        for i in range(end_pos, current_pos, -1):
            # 注意索引是从0开始的，所以是 i-1
            if text[i - 1] in punctuation:
                split_pos = i  # 分割点在标点符号之后
                split_char_pos = i - 1  # 标点符号的位置
                break

        # 根据是否找到标点来决定如何分割
        if split_pos != -1:
            # 情况一：找到了标点，就在标点处分割（但不包含标点符号）
            segment = text[current_pos:split_char_pos]  # 不包含标点符号本身
            current_pos = split_pos
        else:
            # 情况二：未找到标点，执行硬分割
            segment = text[current_pos:end_pos]
            current_pos = end_pos

        # 使用strip()去除分段前后可能存在的空白字符
        segment = segment.strip()
        if segment:  # 只添加非空段落
            # 如果段落末尾有标点符号，移除它
            if segment and segment[-1] in punctuation:
                segment = segment[:-1].strip()
            if segment:  # 再次检查是否为空
                segments.append(segment)

    # 过滤掉可能产生的空字符串
    return [s for s in segments if s]
