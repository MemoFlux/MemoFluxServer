package timing

import (
	"fmt"
	"sync"
	"testing"
	"time"
)

func Routine() {
	var wg sync.WaitGroup
	n := 120000 // 启动的 Goroutine 数量

	// 记录开始时间
	start := time.Now()

	for i := 0; i < n; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			// 模拟 Goroutine 的一些工作（此处简单打印一下）
			_ = i // 这里可以是任务的计算逻辑
		}(i)
	}

	// 等待所有 Goroutines 完成
	wg.Wait()

	// 计算启动时间
	elapsed := time.Since(start)
	fmt.Printf("启动 %d 个 Goroutine 耗时: %v\n", n, elapsed)
}

func BenchmarkRoutine(b *testing.B) {
	Routine()
}
