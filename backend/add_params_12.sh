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
    else
        suffix="实际值"
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
        }"
    
    if [ $? -eq 0 ]; then
        echo "添加成功: ${name}${suffix}"
    else
        echo "添加失败: ${name}${suffix}"
    fi
}

add_param "输出电压" "SV" "VD1000" "Real" "V"
add_param "输出电压" "PV" "VD1004" "Real" "V"
add_param "输出电流" "SV" "VD1008" "Real" "A"
add_param "输出电流" "PV" "VD1012" "Real" "A"
add_param "输出频率" "SV" "VD1016" "Real" "Hz"
add_param "输出频率" "PV" "VD1020" "Real" "Hz"
add_param "输出功率" "SV" "VD1024" "Real" "kW"
add_param "输出功率" "PV" "VD1028" "Real" "kW"
add_param "直流母线电压" "PV" "VD1032" "Real" "V"
add_param "散热器温度" "PV" "VD1036" "Real" "°C"
add_param "IGBT温度" "PV" "VD1040" "Real" "°C"
add_param "输入电压" "PV" "VD1044" "Real" "V"
add_param "运行模式" "SV" "VW1048" "Int" ""
add_param "运行模式" "PV" "VW1050" "Int" ""
add_param "启动指令" "SV" "V1052.0" "Bool" ""
add_param "停止指令" "SV" "V1052.1" "Bool" ""
add_param "故障复位" "SV" "V1052.2" "Bool" ""
add_param "运行状态" "PV" "V1053.0" "Bool" ""
add_param "故障状态" "PV" "V1053.1" "Bool" ""
add_param "报警状态" "PV" "V1053.2" "Bool" ""
add_param "过压保护" "PV" "V1053.3" "Bool" ""
add_param "欠压保护" "PV" "V1053.4" "Bool" ""
add_param "过流保护" "PV" "V1053.5" "Bool" ""
add_param "过载保护" "PV" "V1053.6" "Bool" ""
add_param "过热保护" "PV" "V1053.7" "Bool" ""
add_param "电流上限" "SV" "VD1056" "Real" "A"
add_param "电压上限" "SV" "VD1060" "Real" "V"
add_param "频率上限" "SV" "VD1064" "Real" "Hz"
add_param "功率上限" "SV" "VD1068" "Real" "kW"
add_param "PID比例" "SV" "VD1072" "Real" ""
add_param "PID积分" "SV" "VD1076" "Real" "s"
add_param "PID微分" "SV" "VD1080" "Real" "s"
add_param "加速时间" "SV" "VD1084" "Real" "s"
add_param "减速时间" "SV" "VD1088" "Real" "s"
add_param "脉冲频率" "SV" "VD1092" "Real" "Hz"
add_param "脉冲宽度" "SV" "VD1096" "Real" "%"

echo ""
echo "参数添加完成"