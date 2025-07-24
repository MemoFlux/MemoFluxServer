### 测试文段 1：微信公众号文章截图

**来源:** 微信公众号「AI前沿观察」
**内容:**
> “正如 Bostrom 在其著作《超级智能》中所论述的，对齐问题（Alignment Problem）是当前人工智能安全研究的核心挑战。他认为，一个与人类价值观不完全对齐的超级智能，即使其初始目标是良性的，也可能为了达成目标而采取对人类毁灭性的手段。这构成了所谓的‘工具性趋同’（Instrumental Convergence）理论的基础。”

**预期应用行为:**
*   **自动解析:** 提取文本内容。
*   **自动打标签:** `人工智能伦理`, `对齐问题`, `Bostrom`, `核心论点`, `待引用`。
*   **关联实体:** 识别出人名“Bostrom”和书名“《超级智能》”。

---

### 测试文段 2：PDF 学术论文截图

**来源:** 论文《The Ethics of Artificial Intelligence》, 第 12 页
**内容:**
> **Figure 2.1: Public Trust in AI Systems (2020-2024)**
>
> [此处为一个图表，显示公众对AI信任度逐年下降的数据]
>
> *Source: Stanford HAI 2024 AI Index Report*
>
> The data clearly indicates a growing public skepticism towards autonomous decision-making systems, with trust levels dropping by nearly 15% over the past four years. This trend correlates strongly with high-profile incidents of algorithmic bias in loan applications and hiring.

**预期应用行为:**
*   **自动解析:** 提取图表标题、来源和下方的描述文字。
*   **自动打标签:** `数据支撑`, `公众信任度`, `算法偏见`, `Stanford HAI`。
*   **内容类型识别:** 识别出这是一张“图表”或“数据”。

---

### 测试文段 3：网页新闻报道（分享链接）

**来源:** The Guardian - "EU passes landmark AI Act to regulate artificial intelligence"
**内容:**
> The European Parliament has given final approval to the Artificial Intelligence Act, a comprehensive legal framework that categorizes AI applications based on risk. High-risk systems, such as those used in critical infrastructure or for influencing voters, will face stringent requirements on transparency, data quality, and human oversight. Non-compliance could result in fines of up to €35 million or 7% of a company's global annual turnover.

**预期应用行为:**
*   **自动解析:** 从链接中抓取文章标题和核心摘要。
*   **自动打标签:** `反方观点` (或 `监管政策`), `欧盟AI法案`, `高风险系统`, `合规要求`。
*   **关键信息提取:** 识别出具体的罚款金额“€35 million”和“7% of global annual turnover”。
