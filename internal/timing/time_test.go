package timing

import (
	v1 "MemoFluxServer/api/llm/v1"
	"MemoFluxServer/internal/service"
	"sync"
	"testing"
)

func w1(wg *sync.WaitGroup) {
	defer wg.Done()
	service.GenerateStructSchema(v1.Knowledge{})
}
func w2(wg *sync.WaitGroup) {
	defer wg.Done()
	service.GenerateStructSchema(v1.Schedule{})
}

func BenchmarkStructToJsonSync(b *testing.B) {
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		var wg sync.WaitGroup
		wg.Add(2)
		go w1(&wg)
		go w2(&wg)
		wg.Wait()
	}
}

func BenchmarkJsonToStructNoSync(b *testing.B) {
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		service.GenerateStructSchema(v1.Knowledge{})
		service.GenerateStructSchema(v1.Schedule{})
	}
}
