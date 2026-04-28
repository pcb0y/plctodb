#!/bin/bash

TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjEsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc3NzQ0MDUyMn0.p3Jxd803vVRnLmYoM08Q7JCjqiA3Wxg_h8ZgkHNvC6U"
BASE_URL="http://localhost:8000/api/templates/12/parameters"

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

echo "=== 添加布尔类型故障信号 ==="
add_param "保温时长" "" "C3" "Int" "s"
add_param "主机料温过低" "" "V4551.0" "Bool" ""
add_param "主机料温过低" "" "V4551.1" "Bool" ""
add_param "主机料温过高" "" "V4551.1" "Bool" ""
add_param "主机调速故障" "" "V4551.4" "Bool" ""
add_param "主机过电流" "" "V4550.7" "Bool" ""
add_param "主机料筒冷却风机故障" "" "V4550.2" "Bool" ""
add_param "喂料调速器故障" "" "V4550.1" "Bool" ""
add_param "螺杆故障" "" "V4551.5" "Bool" ""
add_param "喂料过电流" "" "V4553.0" "Bool" ""
add_param "螺杆仓位报警" "" "V4551.3" "Bool" ""
add_param "主机急停未松开" "" "V4551.2" "Bool" ""
add_param "主机风机故障" "" "V4551.6" "Bool" ""
add_param "65主机料温故障" "" "V4553.6" "Bool" ""
add_param "65真空泵故障" "" "V4553.5" "Bool" ""
add_param "35共挤A调速故障" "" "V4551.6" "Bool" ""
add_param "35共挤A过电流" "" "V4553.1" "Bool" ""
add_param "35共挤A料筒冷却风机故障" "" "V4550.1" "Bool" ""
add_param "35共挤B调速故障" "" "V4551.7" "Bool" ""
add_param "35共挤B过电流" "" "V4553.2" "Bool" ""
add_param "35共挤B料筒冷却风机故障" "" "V4550.4" "Bool" ""

echo ""
echo "=== 添加主机转速参数 ==="
add_param "主机转速" "SV" "VD200" "Real" "RPM"
add_param "主机转速" "PV" "VD224" "Real" "RPM"

echo ""
echo "=== 添加主机电流参数 ==="
add_param "主机电流" "SV" "VD232" "Real" "%"
add_param "主机电流" "PV" "VD228" "Real" "A"

echo ""
echo "=== 添加喂料转速参数 ==="
add_param "喂料转速" "SV" "VD204" "Real" "RPM"
add_param "喂料转速" "PV" "VD236" "Real" "RPM"

echo ""
echo "=== 添加喂料电流参数 ==="
add_param "喂料电流" "SV" "VD244" "Real" "%"
add_param "喂料电流" "PV" "VD240" "Real" "A"

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
add_param "65机合流芯" "SV" "VW180" "Int" "°C"
add_param "65机合流芯" "PV" "VW370" "Int" "°C"

echo ""
echo "参数添加完成"