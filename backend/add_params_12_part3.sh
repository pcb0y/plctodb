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

echo "=== 添加A组35机温度参数 ==="
add_param "A组35机1区" "SV" "VW112" "Int" "°C"
add_param "A组35机1区" "PV" "VW312" "Int" "°C"
add_param "A组35机2区" "SV" "VW114" "Int" "°C"
add_param "A组35机2区" "PV" "VW314" "Int" "°C"
add_param "A组35机3区" "SV" "VW116" "Int" "°C"
add_param "A组35机3区" "PV" "VW316" "Int" "°C"

echo ""
echo "=== 添加B组35机温度参数 ==="
add_param "B组35机1区" "SV" "VW118" "Int" "°C"
add_param "B组35机1区" "PV" "VW318" "Int" "°C"
add_param "B组35机2区" "SV" "VW120" "Int" "°C"
add_param "B组35机2区" "PV" "VW320" "Int" "°C"
add_param "B组35机3区" "SV" "VW122" "Int" "°C"
add_param "B组35机3区" "PV" "VW322" "Int" "°C"

echo ""
echo "=== 添加25共挤故障信号 ==="
add_param "25共挤A调速故障" "" "V4550.0" "Bool" ""
add_param "25共挤A过电流" "" "V4553.3" "Bool" ""
add_param "25共挤A料筒冷却风机故障" "" "V4550.5" "Bool" ""
add_param "25共挤B调速故障" "" "V4550.1" "Bool" ""
add_param "25共挤B过电流" "" "V4553.4" "Bool" ""
add_param "25共挤B料筒冷却风机故障" "" "V4550.6" "Bool" ""

echo ""
echo "=== 添加25A转速电流参数 ==="
add_param "25A转速" "SV" "VD216" "Real" "RPM"
add_param "25A转速" "PV" "VD272" "Real" "RPM"
add_param "25A电流" "SV" "VD2300" "Real" "%"
add_param "25A电流" "PV" "VD556" "Real" "A"

echo ""
echo "=== 添加25B转速电流参数 ==="
add_param "25B转速" "SV" "VD220" "Real" "RPM"
add_param "25B转速" "PV" "VD284" "Real" "RPM"
add_param "25B电流" "SV" "VD292" "Real" "%"
add_param "25B电流" "PV" "VD288" "Real" "A"

echo ""
echo "=== 添加A组25机温度参数 ==="
add_param "A组25机1区" "SV" "VW124" "Int" "°C"
add_param "A组25机1区" "PV" "VW324" "Int" "°C"
add_param "A组25机2区" "SV" "VW126" "Int" "°C"
add_param "A组25机2区" "PV" "VW326" "Int" "°C"

echo ""
echo "=== 添加B组25机温度参数 ==="
add_param "B组25机1区" "SV" "VW130" "Int" "°C"
add_param "B组25机1区" "PV" "VW330" "Int" "°C"
add_param "B组25机2区" "SV" "VW132" "Int" "°C"
add_param "B组25机2区" "PV" "VW332" "Int" "°C"

echo ""
echo "参数添加完成"