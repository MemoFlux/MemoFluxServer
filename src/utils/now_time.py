





import datetime


def get_current_date()-> str:
  """
  获取当前日期并以 'YYYY-MM-DD' 格式返回。

  Returns:
      str: 格式为 'YYYY-MM-DD' 的当前日期字符串。
  """
  return datetime.date.today().strftime('%Y-%m-%d')
