package service

import (
	"log"
	"time"
)

func GetNowtime() string {
	location, err := time.LoadLocation("Asia/Shanghai")
	if err != nil {
		log.Fatalf("加载时区失败: %v", err)
	}

	// 2. 获取当前UTC时间
	nowUTC := time.Now().UTC()

	// 3. 将UTC时间转换为东八区时间
	nowBeijing := nowUTC.In(location)
	return nowBeijing.Format("2006-01-02 15:04:05")
}
