package service

import (
	"encoding/json"
	"fmt"
	"reflect"
	"strings"
)

// StructToJSONSchema 接受任何 struct（或指向 struct 的指针）作为输入，
// 并返回其 JSON Schema 表示的 json.RawMessage。
//
// 它使用反射来分析 struct 的字段，并依赖于 struct 标签（tags）来获取元数据：
// - `json:"fieldName,omitempty"`: 用于确定 JSON 输出中的字段名，以及该字段是否可选（omitempty）。
// - `schema:"description:some text"`: 用于为该字段提供描述信息。
func StructToJSONSchema(s interface{}) (json.RawMessage, error) {
	// 获取输入值的反射类型
	val := reflect.ValueOf(s)
	// 如果是指针，获取其指向的元素
	if val.Kind() == reflect.Ptr {
		val = val.Elem()
	}

	// 确保我们处理的是一个 struct
	if val.Kind() != reflect.Struct {
		return nil, fmt.Errorf("input must be a struct or a pointer to a struct, got %s", val.Kind())
	}

	typ := val.Type()

	// 初始化 schema 的基本结构
	schema := map[string]interface{}{
		"type":                 "object",
		"properties":           map[string]interface{}{},
		"additionalProperties": false, // 通常建议禁止未知字段
	}
	required := []string{}
	properties := schema["properties"].(map[string]interface{})

	// 遍历 struct 的所有字段
	for i := 0; i < typ.NumField(); i++ {
		field := typ.Field(i)

		// 跳过非导出的字段（私有字段）
		if field.PkgPath != "" {
			continue
		}

		// 解析 "json" 标签
		jsonTag := field.Tag.Get("json")
		if jsonTag == "" || jsonTag == "-" {
			continue // 如果没有 json 标签或被忽略，则跳过
		}

		tagParts := strings.Split(jsonTag, ",")
		jsonName := tagParts[0]

		// 检查是否包含 "omitempty"
		isOptional := false
		for _, part := range tagParts[1:] {
			if part == "omitempty" {
				isOptional = true
				break
			}
		}

		// 如果字段不是可选的，并且它不是一个指针（指针本身就是可选的），则将其添加到 required 列表
		if !isOptional && field.Type.Kind() != reflect.Ptr {
			required = append(required, jsonName)
		}

		// 创建当前字段的 schema
		propertySchema := make(map[string]interface{})

		// 解析 "schema" 标签以获取描述
		schemaTag := field.Tag.Get("schema")
		if schemaTag != "" {
			// 简单解析 "description:..." 格式
			if strings.HasPrefix(schemaTag, "description:") {
				propertySchema["description"] = strings.TrimSpace(strings.TrimPrefix(schemaTag, "description:"))
			}
		}

		// 解析 "dc" 标签以获取描述（如果 schema 标签没有提供描述的话）
		if _, hasDescription := propertySchema["description"]; !hasDescription {
			dcTag := field.Tag.Get("dc")
			if dcTag != "" {
				propertySchema["description"] = strings.TrimSpace(dcTag)
			}
		}

		// 将 Go 类型映射到 JSON Schema 类型
		if err := mapGoTypeToJSONSchema(field.Type, propertySchema); err != nil {
			return nil, fmt.Errorf("error processing field %s: %w", field.Name, err)
		}

		properties[jsonName] = propertySchema
	}

	// 如果有必填字段，将其添加到 schema 中
	if len(required) > 0 {
		schema["required"] = required
	}

	// 将最终的 schema map 编码为 JSON 字节
	schemaBytes, err := json.Marshal(schema)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal schema to JSON: %w", err)
	}

	// 将 JSON 字节转换为 json.RawMessage 并返回
	return json.RawMessage(schemaBytes), nil
}

// mapGoTypeToJSONSchema 是一个辅助函数，用于将 Go 类型映射到 JSON Schema 属性。
// 它支持递归处理嵌套的 struct 和切片。
func mapGoTypeToJSONSchema(t reflect.Type, schema map[string]interface{}) error {
	// 如果是指针，则获取其基础类型
	if t.Kind() == reflect.Ptr {
		t = t.Elem()
	}

	switch t.Kind() {
	case reflect.String:
		schema["type"] = "string"
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64,
		reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64,
		reflect.Float32, reflect.Float64:
		// 为简化起见，所有数字类型都映射为 "number"
		// 可以进一步区分为 "integer" 和 "number"
		if isInteger(t.Kind()) {
			schema["type"] = "integer"
		} else {
			schema["type"] = "number"
		}
	case reflect.Bool:
		schema["type"] = "boolean"
	case reflect.Slice:
		schema["type"] = "array"
		// 递归处理切片中的元素类型
		itemSchema := make(map[string]interface{})
		if err := mapGoTypeToJSONSchema(t.Elem(), itemSchema); err != nil {
			return fmt.Errorf("error processing slice element type %s: %w", t.Elem().Name(), err)
		}
		schema["items"] = itemSchema
	case reflect.Struct:
		// 对于嵌套的 struct，递归生成其完整的 schema。
		nestedSchemaRaw, err := StructToJSONSchema(reflect.New(t).Interface())
		if err != nil {
			return fmt.Errorf("failed to generate schema for nested struct %s: %w", t.Name(), err)
		}

		var nestedSchema map[string]interface{}
		if err := json.Unmarshal(nestedSchemaRaw, &nestedSchema); err != nil {
			return fmt.Errorf("failed to unmarshal schema for nested struct %s: %w", t.Name(), err)
		}

		// 将嵌套 schema 的属性合并到当前 schema
		for k, v := range nestedSchema {
			schema[k] = v
		}

	default:
		schema["type"] = "string" // 默认或未知类型作为 string 处理
	}
	return nil
}

// isInteger 是一个简单的辅助函数，用于判断一个 Kind 是否为整数类型。
func isInteger(k reflect.Kind) bool {
	return k >= reflect.Int && k <= reflect.Uint64
}
