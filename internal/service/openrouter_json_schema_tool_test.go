package service

import (
	v1 "MemoFluxServer/api/llm/v1"
	"encoding/json"
	"fmt"
	"testing"
)

func TestStructToJSONSchemaWithNestedStructs(t *testing.T) {
	// 测试使用 v1.GeneralRes 结构体，它包含多层嵌套结构体
	generalRes := v1.GeneralRes{}

	schema, err := StructToJSONSchema(generalRes)
	if err != nil {
		t.Fatalf("Failed to generate schema: %v", err)
	}

	// 美化输出 JSON Schema
	var prettySchema map[string]interface{}
	if err := json.Unmarshal(schema, &prettySchema); err != nil {
		t.Fatalf("Failed to unmarshal schema: %v", err)
	}

	prettyJSON, err := json.MarshalIndent(prettySchema, "", "  ")
	if err != nil {
		t.Fatalf("Failed to marshal pretty JSON: %v", err)
	}

	fmt.Println("Generated JSON Schema for v1.GeneralRes:")
	fmt.Println(string(prettyJSON))
}

func TestStructToJSONSchemaSimpleStruct(t *testing.T) {
	// 创建一个简单的测试结构体
	type SimpleStruct struct {
		Name    string `json:"name" schema:"description:用户姓名"`
		Age     int    `json:"age" schema:"description:用户年龄"`
		IsAdmin bool   `json:"isAdmin,omitempty" schema:"description:是否为管理员"`
	}

	simple := SimpleStruct{}
	schema, err := StructToJSONSchema(simple)
	if err != nil {
		t.Fatalf("Failed to generate schema for simple struct: %v", err)
	}

	var prettySchema map[string]interface{}
	if err := json.Unmarshal(schema, &prettySchema); err != nil {
		t.Fatalf("Failed to unmarshal schema: %v", err)
	}

	prettyJSON, err := json.MarshalIndent(prettySchema, "", "  ")
	if err != nil {
		t.Fatalf("Failed to marshal pretty JSON: %v", err)
	}

	fmt.Println("\nGenerated JSON Schema for SimpleStruct:")
	fmt.Println(string(prettyJSON))
}

func TestStructToJSONSchemaNestedArray(t *testing.T) {
	// 创建一个包含嵌套结构体数组的测试结构体
	type Address struct {
		Street  string `json:"street" schema:"description:街道地址"`
		City    string `json:"city" schema:"description:城市"`
		ZipCode string `json:"zipCode,omitempty" schema:"description:邮政编码"`
	}

	type Person struct {
		Name      string    `json:"name" schema:"description:姓名"`
		Age       int       `json:"age" schema:"description:年龄"`
		Addresses []Address `json:"addresses" schema:"description:地址列表"`
	}

	person := Person{}
	schema, err := StructToJSONSchema(person)
	if err != nil {
		t.Fatalf("Failed to generate schema for nested array struct: %v", err)
	}

	var prettySchema map[string]interface{}
	if err := json.Unmarshal(schema, &prettySchema); err != nil {
		t.Fatalf("Failed to unmarshal schema: %v", err)
	}

	prettyJSON, err := json.MarshalIndent(prettySchema, "", "  ")
	if err != nil {
		t.Fatalf("Failed to marshal pretty JSON: %v", err)
	}

	fmt.Println("\nGenerated JSON Schema for Person with Address array:")
	fmt.Println(string(prettyJSON))
}
