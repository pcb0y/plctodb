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

echo "=== 添加25B故障信号 ==="
add_param "25B调速故障" "" "V4550.1" "Bool" ""
add_param "25B过电流" "" "V4550.7" "Bool" ""
add_param "25B料筒冷却风机故障" "" "V4550.4" "Bool" ""
add_param "25A调速故障" "" "V4551.4" "Bool" ""
add_param "25A过电流" "" "V4551.7" "Bool" ""
add_param "25A料筒冷却风机故障" "" "V4550.6" "Bool" ""

echo ""
echo "=== 添加25B转速电流参数 ==="
add_param "25B转速" "SV" "VD212" "Real" "RPM"
add_param "25B转速" "PV" "VD532" "Real" "RPM"
add_param "25B电流" "SV" "VD2300" "Real" "%"
add_param "25B电流" "PV" "VD556" "Real" "A"

echo ""
echo "=== 添加25A转速电流参数 ==="
add_param "25A转速" "SV" "VD532" "Real" "RPM"
add_param "25A转速" "PV" "VD232" "Real" "RPM"
add_param "25A电流" "SV" "VD3300" "Real" "%"
add_param "25A电流" "PV" "VD256" "Real" "A"

echo ""
echo "=== 添加B组25机温度参数 ==="
add_param "B组25机1区" "SV" "VW102" "Int" "°C"
add_param "B组25机1区" "PV" "VW302" "Int" "°C"
add_param "B组25机2区" "SV" "VW104" "Int" "°C"
add_param "B组25机2区" "PV" "VW304" "Int" "°C"
add_param "B组25机3区" "SV" "VW106" "Int" "°C"
add_param "B组25机3区" "PV" "VW306" "Int" "°C"

echo ""
echo "=== 添加A组25机温度参数 ==="
add_param "A组25机1区" "SV" "VW108" "Int" "°C"
add_param "A组25机1区" "PV" "VW308" "Int" "°C"
add_param "A组25机2区" "SV" "VW116" "Int" "°C"
add_param "A组25机2区" "PV" "VW316" "Int" "°C"
add_param "A组25机3区" "SV" "VW118" "Int" "°C"
add_param "A组25机3区" "PV" "VW318" "Int" "°C"

echo ""
echo "=== 添加25B共挤备用参数 ==="
add_param "25B共挤备用1" "SV" "VW1130" "Int" "°C"
add_param "25B共挤备用1" "PV" "VW330" "Int" "°C"
add_param "25B共挤备用2" "SV" "VW1132" "Int" "°C"
add_param "25B共挤备用2" "PV" "VW332" "Int" "°C"

echo ""
echo "=== 添加25A共挤备用参数 ==="
add_param "25A共挤备用1" "SV" "VW1134" "Int" "°C"
add_param "25A共挤备用1" "PV" "VW334" "Int" "°C"
add_param "25A共挤备用2" "SV" "VW1136" "Int" "°C"
add_param "25A共挤备用2" "PV" "VW336" "Int" "°C"

echo ""
echo "参数添加完成"