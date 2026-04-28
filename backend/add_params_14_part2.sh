#!/bin/bash

TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjEsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc3NzQ0MDUyMn0.p3Jxd803vVRnLmYoM08Q7JCjqiA3Wxg_h8ZgkHNvC6U"
BASE_URL="http://localhost:8000/api/templates/14/parameters"

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
add_param "外层模具下" "SV" "VW1140" "Int" "°C"
add_param "外层模具下" "PV" "VW340" "Int" "°C"
add_param "外层模具左" "SV" "VW1142" "Int" "°C"
add_param "外层模具左" "PV" "VW342" "Int" "°C"
add_param "外层模具右" "SV" "VW1144" "Int" "°C"
add_param "外层模具右" "PV" "VW344" "Int" "°C"

echo ""
echo "=== 添加A组合流芯温度参数 ==="
add_param "A组合流芯" "SV" "VW1146" "Int" "°C"
add_param "A组合流芯" "PV" "VW346" "Int" "°C"
add_param "A组转接模" "SV" "VW1148" "Int" "°C"
add_param "A组转接模" "PV" "VW348" "Int" "°C"
add_param "A组连接管" "SV" "VW1150" "Int" "°C"
add_param "A组连接管" "PV" "VW350" "Int" "°C"

echo ""
echo "=== 添加B组合流芯温度参数 ==="
add_param "B组合流芯" "SV" "VW1152" "Int" "°C"
add_param "B组合流芯" "PV" "VW352" "Int" "°C"
add_param "B组转接模" "SV" "VW1162" "Int" "°C"
add_param "B组转接模" "PV" "VW362" "Int" "°C"
add_param "B组连接管" "SV" "VW1164" "Int" "°C"
add_param "B组连接管" "PV" "VW364" "Int" "°C"

echo ""
echo "=== 添加35A转速电流参数 ==="
add_param "35A转速" "SV" "VD508" "Real" "RPM"
add_param "35A转速" "PV" "VD532" "Real" "RPM"
add_param "35A电流" "SV" "VD2300" "Real" "%"
add_param "35A电流" "PV" "VD556" "Real" "A"

echo ""
echo "=== 添加35B转速电流参数 ==="
add_param "35B转速" "SV" "VD212" "Real" "RPM"
add_param "35B转速" "PV" "VD236" "Real" "RPM"
add_param "35B电流" "SV" "VD3308" "Real" "%"
add_param "35B电流" "PV" "VD264" "Real" "A"

echo ""
echo "=== 添加A组35机温度参数 ==="
add_param "A组35机1区" "SV" "VW116" "Int" "°C"
add_param "A组35机1区" "PV" "VW316" "Int" "°C"
add_param "A组35机2区" "SV" "VW118" "Int" "°C"
add_param "A组35机2区" "PV" "VW318" "Int" "°C"
add_param "A组35机3区" "SV" "VW168" "Int" "°C"
add_param "A组35机3区" "PV" "VW368" "Int" "°C"

echo ""
echo "=== 添加B组35机温度参数 ==="
add_param "B组35机1区" "SV" "VW170" "Int" "°C"
add_param "B组35机1区" "PV" "VW370" "Int" "°C"
add_param "B组35机2区" "SV" "VW120" "Int" "°C"
add_param "B组35机2区" "PV" "VW322" "Int" "°C"
add_param "B组35机3区" "SV" "VW112" "Int" "°C"
add_param "B组35机3区" "PV" "VW312" "Int" "°C"

echo ""
echo "参数添加完成"