package service

import (
	"fmt"
	"reflect"
	"strings"
)

// GenerateStructSchema 是我们最终要调用的函数。
// 它接收任何 struct 的零值（如 User{}），然后输出描述其结构的字符串。
func GenerateStructSchema(s interface{}) (string, error) {
	t := reflect.TypeOf(s)

	// 确保输入的是 struct 或指向 struct 的指针
	if t.Kind() == reflect.Ptr {
		t = t.Elem()
	}
	if t.Kind() != reflect.Struct {
		return "", fmt.Errorf("input must be a struct, but got %s", t.Kind())
	}

	var sb strings.Builder
	sb.WriteString("{\n")
	// 调用递归辅助函数来生成字段列表
	sb.WriteString(generateFieldsString(t, 1))
	sb.WriteString("}")

	return sb.String(), nil
}

// generateFieldsString 是一个递归辅助函数，用于生成结构体的字段字符串。
// indentLevel 控制缩进层级。
func generateFieldsString(t reflect.Type, indentLevel int) string {
	var sb strings.Builder
	indent := strings.Repeat("  ", indentLevel)

	for i := 0; i < t.NumField(); i++ {
		field := t.Field(i)

		// 跳过非导出字段（重要！）
		if !field.IsExported() {
			continue
		}

		// 从 `desc` 标签获取注释
		descTag := field.Tag.Get("dc")
		if descTag != "" {
			sb.WriteString(fmt.Sprintf("%s// %s\n", indent, descTag))
		}

		// 获取字段名（首字母转为小写）
		fieldName := strings.ToLower(string(field.Name[0])) + string(field.Name[1:])

		// 递归获取类型字符串
		typeString := mapGoTypeToTS(field.Type, indentLevel)

		sb.WriteString(fmt.Sprintf("%s%s: %s,\n", indent, fieldName, typeString))
	}

	return sb.String()
}

// mapGoTypeToTS 将 Go 的 reflect.Type 转换为我们想要的类型字符串。
func mapGoTypeToTS(t reflect.Type, indentLevel int) string {
	switch t.Kind() {
	case reflect.String:
		return "string"
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64,
		reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64,
		reflect.Float32, reflect.Float64:
		return "number"
	case reflect.Bool:
		return "boolean"
	case reflect.Slice:
		// 递归处理切片内的元素类型
		elemType := mapGoTypeToTS(t.Elem(), indentLevel)
		return fmt.Sprintf("%s[]", elemType)
	case reflect.Ptr:
		// 递归处理指针指向的类型
		return mapGoTypeToTS(t.Elem(), indentLevel)
	case reflect.Struct:
		// 递归处理嵌套的 struct
		var sb strings.Builder
		sb.WriteString("{\n")
		sb.WriteString(generateFieldsString(t, indentLevel+1))
		sb.WriteString(strings.Repeat("  ", indentLevel) + "}")
		return sb.String()
	default:
		return "any"
	}
}
