#!/bin/bash

TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjEsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc3NzQ0MDUyMn0.p3Jxd803vVRnLmYoM08Q7JCjqiA3Wxg_h8ZgkHNvC6U"
BASE_URL="http://localhost:8000/api/templates/13/parameters"

add_param() {
    local name=$1
    local type=$2
    local address=$3
    local data_type=$4
    local unit=$5
    
    if [ "$type" = "SV" ]; then
        suffix="设定值"
        is_readonly="false"
    elif [ "$type" = "PV" ]; then
        suffix="实际值"
        is_readonly="true"
    else
        suffix=""
        is_readonly="true"
    fi
    
    curl -s -X POST "$BASE_URL" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"parameter_name\": \"${name}${suffix}\",
            \"parameter_address\": \"$address\",
            \"parameter_value\": \"\",
            \"parameter_unit\": \"$unit\",
            \"parameter_type\": \"$data_type\",
            \"is_readonly\": $is_readonly
        }" > /dev/null
    
    if [ $? -eq 0 ]; then
        echo "添加成功: ${name}${suffix}"
    else
        echo "添加失败: ${name}${suffix}"
    fi
}

echo "=== 添加基础信号参数 ==="
add_param "保温时长" "" "C3" "Int" "s"
add_param "主机料温过低" "" "V4551.2" "Bool" ""
add_param "主机料温过高" "" "V4551.1" "Bool" ""
add_param "主机调速故障" "" "V4551.4" "Bool" ""
add_param "主机过电流" "" "V4551.7" "Bool" ""
add_param "主机过载" "" "V4550.6" "Bool" ""
add_param "主机料筒冷却风机故障" "" "V4550.4" "Bool" ""
add_param "喂料调速器故障" "" "V4553.0" "Bool" ""
add_param "喂料过电流" "" "V4553.1" "Bool" ""
add_param "螺杆仓位报警" "" "V4551.3" "Bool" ""
add_param "主机急停未松开" "" "V4551.0" "Bool" ""
add_param "主机调速报警" "" "V4550.1" "Bool" ""
add_param "35A调速故障" "" "V4550.1" "Bool" ""
add_param "35A过电流" "" "V4550.7" "Bool" ""
add_param "35A料筒冷却风机故障" "" "V4550.6" "Bool" ""
add_param "35B调速故障" "" "V4550.5" "Bool" ""
add_param "35B过电流" "" "V4550.0" "Bool" ""
add_param "35B料筒冷却风机故障" "" "V4553.2" "Bool" ""

echo ""
echo "=== 添加主机转速参数 ==="
add_param "主机转速" "SV" "VD208" "Real" "RPM"
add_param "主机转速" "PV" "VD232" "Real" "RPM"

echo ""
echo "=== 添加主机电流参数 ==="
add_param "主机电流" "SV" "VD3300" "Real" "%"
add_param "主机电流" "PV" "VD256" "Real" "A"

echo ""
echo "=== 添加喂料转速参数 ==="
add_param "喂料转速" "SV" "VD32" "Real" "RPM"
add_param "喂料转速" "PV" "VD244" "Real" "RPM"

echo ""
echo "=== 添加喂料电流参数 ==="
add_param "喂料电流" "SV" "VD3304" "Real" "%"
add_param "喂料电流" "PV" "VD260" "Real" "A"

echo ""
echo "=== 添加65机筒温度参数 ==="
add_param "65机筒1区" "SV" "VW102" "Int" "°C"
add_param "65机筒1区" "PV" "VW302" "Int" "°C"
add_param "65机筒2区" "SV" "VW104" "Int" "°C"
add_param "65机筒2区" "PV" "VW304" "Int" "°C"
add_param "65机筒3区" "SV" "VW106" "Int" "°C"
add_param "65机筒3区" "PV" "VW306" "Int" "°C"
add_param "65机筒4区" "SV" "VW108" "Int" "°C"
add_param "65机筒4区" "PV" "VW308" "Int" "°C"
add_param "65机筒流芯" "SV" "VW154" "Int" "°C"
add_param "65机筒流芯" "PV" "VW354" "Int" "°C"
add_param "65机合流芯" "SV" "VW130" "Int" "°C"
add_param "65机合流芯" "PV" "VW330" "Int" "°C"

echo ""
echo "=== 添加芯层模具温度参数 ==="
add_param "芯层模具上" "SV" "VW1130" "Int" "°C"
add_param "芯层模具上" "PV" "VW330" "Int" "°C"
add_param "芯层模具下" "SV" "VW1132" "Int" "°C"
add_param "芯层模具下" "PV" "VW332" "Int" "°C"
add_param "芯层模具左" "SV" "VW1134" "Int" "°C"
add_param "芯层模具左" "PV" "VW334" "Int" "°C"
add_param "芯层模具右" "SV" "VW1136" "Int" "°C"
add_param "芯层模具右" "PV" "VW336" "Int" "°C"

echo ""
echo "=== 添加外层模具温度参数 ==="
add_param "外层模具上" "SV" "VW1138" "Int" "°C"
add_param "外层模具上" "PV" "VW338" "Int" "°C"

echo ""
echo "参数添加完成"