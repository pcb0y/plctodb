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

echo "=== 添加芯层模具温度参数 ==="
add_param "芯层模具上" "SV" "VW140" "Int" "°C"
add_param "芯层模具上" "PV" "VW330" "Int" "°C"
add_param "芯层模具下" "SV" "VW142" "Int" "°C"
add_param "芯层模具下" "PV" "VW332" "Int" "°C"
add_param "芯层模具左" "SV" "VW144" "Int" "°C"
add_param "芯层模具左" "PV" "VW334" "Int" "°C"
add_param "芯层模具右" "SV" "VW146" "Int" "°C"
add_param "芯层模具右" "PV" "VW336" "Int" "°C"

echo ""
echo "=== 添加外层模具温度参数 ==="
add_param "外层模具上" "SV" "VW148" "Int" "°C"
add_param "外层模具上" "PV" "VW338" "Int" "°C"
add_param "外层模具下" "SV" "VW150" "Int" "°C"
add_param "外层模具下" "PV" "VW340" "Int" "°C"
add_param "外层模具左" "SV" "VW152" "Int" "°C"
add_param "外层模具左" "PV" "VW342" "Int" "°C"
add_param "外层模具右" "SV" "VW154" "Int" "°C"
add_param "外层模具右" "PV" "VW344" "Int" "°C"

echo ""
echo "=== 添加A组温度参数 ==="
add_param "A组合流芯" "SV" "VW156" "Int" "°C"
add_param "A组合流芯" "PV" "VW346" "Int" "°C"
add_param "A组转接模" "SV" "VW158" "Int" "°C"
add_param "A组转接模" "PV" "VW348" "Int" "°C"
add_param "A组连接管" "SV" "VW160" "Int" "°C"
add_param "A组连接管" "PV" "VW350" "Int" "°C"

echo ""
echo "=== 添加B组温度参数 ==="
add_param "B组合流芯" "SV" "VW162" "Int" "°C"
add_param "B组合流芯" "PV" "VW352" "Int" "°C"
add_param "B组转接模" "SV" "VW164" "Int" "°C"
add_param "B组转接模" "PV" "VW354" "Int" "°C"
add_param "B组连接管" "SV" "VW166" "Int" "°C"
add_param "B组连接管" "PV" "VW356" "Int" "°C"

echo ""
echo "=== 添加备用参数 ==="
add_param "备用1" "SV" "VW168" "Int" "°C"
add_param "备用1" "PV" "VW358" "Int" "°C"
add_param "备用2" "SV" "VW170" "Int" "°C"
add_param "备用2" "PV" "VW360" "Int" "°C"

echo ""
echo "=== 添加35A转速电流参数 ==="
add_param "35A转速" "SV" "VD208" "Real" "RPM"
add_param "35A转速" "PV" "VD248" "Real" "RPM"
add_param "35A电流" "SV" "VD256" "Real" "%"
add_param "35A电流" "PV" "VD252" "Real" "A"

echo ""
echo "=== 添加35B转速电流参数 ==="
add_param "35B转速" "SV" "VD212" "Real" "RPM"
add_param "35B转速" "PV" "VD260" "Real" "RPM"
add_param "35B电流" "SV" "VD268" "Real" "%"
add_param "35B电流" "PV" "VD264" "Real" "A"

echo ""
echo "参数添加完成"