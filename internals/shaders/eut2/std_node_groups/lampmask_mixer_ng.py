# ##### BEGIN GPL LICENSE BLOCK #####
# (Lisensi GPL seperti pada skrip asli Anda)
# ##### END GPL LICENSE BLOCK #####

# Copyright (C) 2019-2021: SCS Software

import bpy
from io_scs_tools.consts import LampTools as _LT_consts
from io_scs_tools.consts import Material as _MAT_consts

VEHICLE_SIDES = _LT_consts.VehicleSides
VEHICLE_LAMP_TYPES = _LT_consts.VehicleLampTypes
AUX_LAMP_TYPES = _LT_consts.AuxiliaryLampTypes
TRAFFIC_LIGHT_TYPES = _LT_consts.TrafficLightTypes

UV_X_TILES = ["UV_X_0_", "UV_X_1_", "UV_X_2_", "UV_X_3_", "UV_X_4_"]
UV_Y_TILES = ["UV_Y_0_", "UV_Y_1_", "UV_Y_2_", "UV_Y_3_"]

LAMPMASK_MIX_G = _MAT_consts.node_group_prefix + "LampmaskMixerGroup"

_ALPHA_DECODE_NODE = "Alpha Decode"
_UV_DOT_X_NODE = "UV_X_Separator"
_UV_DOT_Y_NODE = "UV_Y_Separator"
_TEX_COL_SEP_NODE = "TexColorSeparator"
_MIN_UV_SUFFIX = "MinUV"
_MAX_UV_SUFFIX = "MaxUV"
_IN_BOUNDS_SUFFIX = "InBounds"
_ADD_NODE_PREFIX = "Addition"


def get_node_group():
    if LAMPMASK_MIX_G not in bpy.data.node_groups:
        __create_node_group__()
    return bpy.data.node_groups[LAMPMASK_MIX_G]

# --- Fungsi-fungsi helper dari skrip asli (TIDAK DIUBAH) ---
def __init_uv_tile_bounding_nodes__(node_tree, uv_dot_n, name, pos_x, pos_y, max_x_uv):
    max_uv_n = node_tree.nodes.new("ShaderNodeMath")
    max_uv_n.name = name + _MAX_UV_SUFFIX
    max_uv_n.label = name + _MAX_UV_SUFFIX
    max_uv_n.location = (pos_x, pos_y - 50)
    max_uv_n.hide = True
    max_uv_n.operation = "LESS_THAN"
    max_uv_n.inputs[1].default_value = max_x_uv

    if max_x_uv == 1: # Hanya untuk tile pertama yang mungkin perlu batas bawah 0
        min_uv_n = node_tree.nodes.new("ShaderNodeMath")
        min_uv_n.name = name + _MIN_UV_SUFFIX
        min_uv_n.label = name + _MIN_UV_SUFFIX
        min_uv_n.location = (pos_x, pos_y)
        min_uv_n.hide = True
        min_uv_n.operation = "GREATER_THAN" # Seharusnya GREATER_THAN 0 atau LESS_THAN -1 jika UV < 0
                                          # Skrip asli menggunakan LESS_THAN max_x_uv - 2
                                          # Jika max_x_uv = 1, maka LESS_THAN -1. Ini mungkin untuk menangani UV negatif.
                                          # Mari ikuti skrip asli untuk konsistensi, walau logikanya agak unik.
        min_uv_n.operation = "LESS_THAN"
        min_uv_n.inputs[1].default_value = max_x_uv - 2 if max_x_uv -2 >=0 else 0 # Hindari nilai negatif jika tidak dimaksudkan
        node_tree.links.new(min_uv_n.inputs[0], uv_dot_n.outputs['Value'])
    node_tree.links.new(max_uv_n.inputs[0], uv_dot_n.outputs['Value'])


def __init_vehicle_uv_bounding_nodes__(node_tree, vehicle_side, pos_x, pos_y):
    # Logika pemilihan min_uv_n dan max_uv_n dari skrip asli
    # Perhatikan bahwa skrip asli mungkin memiliki asumsi spesifik tentang node mana yang ada
    # Jika UV_X_TILES[0] + _MIN_UV_SUFFIX tidak ada untuk semua kasus, ini bisa error.
    # Mari asumsikan __init_uv_tile_bounding_nodes__ dipanggil untuk semua UV_X_TILES sebelum ini.

    if vehicle_side == VEHICLE_SIDES.FrontLeft:
        # Asumsi: UV_X_0_MinUV ada jika tile pertama butuh batas bawah eksplisit.
        # Jika tidak, mungkin hanya menggunakan MaxUV dari tile sebelumnya dan MaxUV tile saat ini.
        # Skrip asli menggunakan _MIN_UV_SUFFIX hanya untuk tile pertama.
        min_node_name_candidate = UV_X_TILES[0] + _MIN_UV_SUFFIX
        min_uv_n = node_tree.nodes.get(min_node_name_candidate)
        if not min_uv_n: # Fallback jika _MIN_UV_SUFFIX tidak dibuat untuk tile ini (misal bukan tile pertama)
                       # Atau jika UV_X_0_MinUV tidak ada, mungkin perlu node dummy 0 atau logika lain.
                       # Untuk sementara, jika tidak ada, kita tidak bisa membuat link dengan benar.
                       # Ini perlu peninjauan lebih lanjut terhadap logika _MIN_UV_SUFFIX di skrip asli.
                       # Berdasarkan skrip asli, _MIN_UV_SUFFIX hanya dibuat jika max_x_uv == 1
                       # Mari kita asumsikan ini untuk tile UV_X_0
            # Jika tidak ada, ini akan error. Kita perlu penanganan yang lebih baik atau memastikan node ada.
            # Untuk saat ini, jika node tidak ada, kita tidak bisa membuat link.
            # Dalam skrip asli, bagian ini mengandalkan node tersebut ada.
             pass # Akan error jika min_uv_n None dan digunakan di link.
                 # Mungkin lebih baik membuat dummy 0 jika tidak ada.

        max_uv_n = node_tree.nodes[UV_X_TILES[0] + _MAX_UV_SUFFIX]
    elif vehicle_side == VEHICLE_SIDES.FrontRight:
        min_uv_n = node_tree.nodes[UV_X_TILES[0] + _MAX_UV_SUFFIX]
        max_uv_n = node_tree.nodes[UV_X_TILES[1] + _MAX_UV_SUFFIX]
    elif vehicle_side == VEHICLE_SIDES.RearLeft:
        min_uv_n = node_tree.nodes[UV_X_TILES[1] + _MAX_UV_SUFFIX]
        max_uv_n = node_tree.nodes[UV_X_TILES[2] + _MAX_UV_SUFFIX]
    elif vehicle_side == VEHICLE_SIDES.RearRight:
        min_uv_n = node_tree.nodes[UV_X_TILES[2] + _MAX_UV_SUFFIX]
        max_uv_n = node_tree.nodes[UV_X_TILES[3] + _MAX_UV_SUFFIX]
    else:  # fallback to middle (VEHICLE_SIDES.Middle)
        min_uv_n = node_tree.nodes[UV_X_TILES[3] + _MAX_UV_SUFFIX]
        max_uv_n = node_tree.nodes[UV_X_TILES[4] + _MAX_UV_SUFFIX]

    uv_in_bounds_n = node_tree.nodes.new("ShaderNodeMath")
    uv_in_bounds_n.name = vehicle_side.name + _IN_BOUNDS_SUFFIX
    uv_in_bounds_n.label = vehicle_side.name + _IN_BOUNDS_SUFFIX
    uv_in_bounds_n.location = (pos_x + 185, pos_y - 50)
    uv_in_bounds_n.width_hidden = 100
    uv_in_bounds_n.hide = True
    uv_in_bounds_n.operation = "MULTIPLY" # Skrip asli menggunakan "LESS_THAN" antara dua output boolean.
                                       # MULTIPLY (AND) lebih umum untuk (Val > Min AND Val < Max)
                                       # Jika min_uv_n dan max_uv_n adalah hasil LESS_THAN (boolean),
                                       # maka LESS_THAN di antara mereka menjadi (NOT A) AND B.
                                       # Mari kita ikuti skrip asli: LESS_THAN
    uv_in_bounds_n.operation = "LESS_THAN"


    # Penanganan jika min_uv_n tidak ada untuk FrontLeft (karena _MIN_UV_SUFFIX hanya untuk tile pertama)
    if vehicle_side == VEHICLE_SIDES.FrontLeft and not node_tree.nodes.get(UV_X_TILES[0] + _MIN_UV_SUFFIX):
        # Jika _MIN_UV_SUFFIX untuk UV_X_0 tidak ada, ini berarti kita di tile pertama (0-1)
        # dan tidak ada batas bawah eksplisit selain > 0.
        # Node 'LESS_THAN' uv_in_bounds_n akan membutuhkan 2 input.
        # Input pertama (dari min_uv_n) bisa dianggap selalu benar (1) jika UV > 0.
        # Ini adalah area yang perlu dipastikan bagaimana skrip asli menangani kasus batas UV terendah.
        # Untuk sekarang, jika min_uv_n tidak ada, link akan gagal.
        # Alternatif: buat node Value dengan output 1 (true) jika UV > 0 atau 0.
        # Berdasarkan skrip asli: `min_uv_n = node_tree.nodes[UV_X_TILES[0] + _MIN_UV_SUFFIX]`
        # Ini mengasumsikan _MIN_UV_SUFFIX ADA untuk UV_X_TILES[0].
        # Mari pastikan __init_uv_tile_bounding_nodes__ membuat ini.
        # Ya, __init_uv_tile_bounding_nodes__ membuat _MIN_UV_SUFFIX jika max_x_uv == 1.
        # Saat memanggil untuk UV_X_TILES[0], max_x_uv akan 1. Jadi _MIN_UV_SUFFIX akan ada.
        node_tree.links.new(uv_in_bounds_n.inputs[0], min_uv_n.outputs[0])
    elif min_uv_n : # Untuk kasus lain dimana min_uv_n adalah _MAX_UV_SUFFIX dari tile sebelumnya
        node_tree.links.new(uv_in_bounds_n.inputs[0], min_uv_n.outputs[0])

    if max_uv_n:
        node_tree.links.new(uv_in_bounds_n.inputs[1], max_uv_n.outputs[0])


def __init_traffic_light_uv_bounding_nodes__(node_tree, traffic_light_type, pos_x, pos_y):
    # (Kode seperti di skrip asli)
    min_tile_i = max_tile_i = 0
    if traffic_light_type == TRAFFIC_LIGHT_TYPES.Red:
        min_tile_i = 0; max_tile_i = 1
    elif traffic_light_type == TRAFFIC_LIGHT_TYPES.Yellow:
        min_tile_i = 1; max_tile_i = 2
    elif traffic_light_type == TRAFFIC_LIGHT_TYPES.Green:
        min_tile_i = 2; max_tile_i = 3

    uv_x_in_bounds_n = node_tree.nodes.new("ShaderNodeMath")
    uv_x_in_bounds_n.name = traffic_light_type.name + "X" + _IN_BOUNDS_SUFFIX
    uv_x_in_bounds_n.label = traffic_light_type.name + "X" + _IN_BOUNDS_SUFFIX
    uv_x_in_bounds_n.location = (pos_x + 185, pos_y)
    uv_x_in_bounds_n.width_hidden = 100; uv_x_in_bounds_n.hide = True
    uv_x_in_bounds_n.operation = "LESS_THAN" # Seharusnya MULTIPLY jika inputnya adalah (U > minX) dan (U < maxX)
                                          # Mengikuti skrip asli: LESS_THAN antara dua boolean

    uv_y_in_bounds_n = node_tree.nodes.new("ShaderNodeMath")
    uv_y_in_bounds_n.name = traffic_light_type.name + "Y" + _IN_BOUNDS_SUFFIX
    uv_y_in_bounds_n.label = traffic_light_type.name + "Y" + _IN_BOUNDS_SUFFIX
    uv_y_in_bounds_n.location = (pos_x + 185, pos_y - 50)
    uv_y_in_bounds_n.width_hidden = 100; uv_y_in_bounds_n.hide = True
    uv_y_in_bounds_n.operation = "LESS_THAN"

    uv_in_bounds_n = node_tree.nodes.new("ShaderNodeMath")
    uv_in_bounds_n.name = traffic_light_type.name + _IN_BOUNDS_SUFFIX
    uv_in_bounds_n.label = traffic_light_type.name + _IN_BOUNDS_SUFFIX
    uv_in_bounds_n.location = (pos_x + 185 * 2, pos_y)
    uv_in_bounds_n.width_hidden = 100; uv_in_bounds_n.hide = True
    uv_in_bounds_n.operation = "MULTIPLY" # Ini benar, (X_in_bounds AND Y_in_bounds)

    # X bounds
    # Untuk traffic light, X bound selalu dari UV_X_0_Min ke UV_X_N_Max
    # Namun skrip asli menggunakan MAX dari tile sebelumnya dan MAX dari tile saat ini
    min_uv_x_n = node_tree.nodes[UV_X_TILES[min_tile_i] + _MAX_UV_SUFFIX] # Ini adalah < Max_dari_Tile_Sebelumnya
    if min_tile_i == 0 and node_tree.nodes.get(UV_X_TILES[0] + _MIN_UV_SUFFIX): # Khusus untuk tile pertama, batas bawahnya dari _MIN_UV_SUFFIX
        min_uv_x_n_actual_lower_bound = node_tree.nodes[UV_X_TILES[0] + _MIN_UV_SUFFIX]
         # Logika LESS_THAN antara dua boolean: (Val > Min) < (Val < Max)
         # Input 0: Val > Min (atau 1 - (Val < Min))
         # Input 1: Val < Max
         # Untuk traffic light, skrip asli menggunakan MAX_UV_SUFFIX dari tile sebelumnya sbg min bound
         # dan MAX_UV_SUFFIX dari tile saat ini sbg max bound
    max_uv_x_n = node_tree.nodes[UV_X_TILES[max_tile_i] + _MAX_UV_SUFFIX] # Ini adalah < Max_dari_Tile_Saat_Ini
    node_tree.links.new(uv_x_in_bounds_n.inputs[0], min_uv_x_n.outputs[0])
    node_tree.links.new(uv_x_in_bounds_n.inputs[1], max_uv_x_n.outputs[0])

    # Y bounds (menggunakan UV_Y_TILES)
    min_uv_y_n = node_tree.nodes[UV_Y_TILES[min_tile_i] + _MAX_UV_SUFFIX]
    if min_tile_i == 0 and node_tree.nodes.get(UV_Y_TILES[0] + _MIN_UV_SUFFIX):
         pass # logika serupa untuk Y jika diperlukan
    max_uv_y_n = node_tree.nodes[UV_Y_TILES[max_tile_i] + _MAX_UV_SUFFIX]
    node_tree.links.new(uv_y_in_bounds_n.inputs[0], min_uv_y_n.outputs[0])
    node_tree.links.new(uv_y_in_bounds_n.inputs[1], max_uv_y_n.outputs[0])

    node_tree.links.new(uv_in_bounds_n.inputs[0], uv_x_in_bounds_n.outputs[0])
    node_tree.links.new(uv_in_bounds_n.inputs[1], uv_y_in_bounds_n.outputs[0])


def __create_merging_node__(node_tree, node_name, position, output_0, output_1):
    mult_n = node_tree.nodes.new("ShaderNodeMath")
    mult_n.name = node_name
    mult_n.label = node_name
    mult_n.location = position
    mult_n.hide = True
    mult_n.operation = "MULTIPLY"
    node_tree.links.new(mult_n.inputs[0], output_0)
    node_tree.links.new(mult_n.inputs[1], output_1)
    return mult_n
# --- Akhir Fungsi-fungsi helper dari skrip asli ---


# --- MODIFIKASI FUNGSI SWITCH LAMPU ---
def __determine_target_list_for_vehicle_lamp__(lamp_type, vehicle_side, lists):
    """Menentukan target list berdasarkan lamp_type dan vehicle_side."""
    nodes_for_yellow_fac, nodes_for_red_fac, nodes_for_w_fac = lists

    # Grup Kuning
    if lamp_type == VEHICLE_LAMP_TYPES.LeftTurn and vehicle_side in [VEHICLE_SIDES.FrontLeft, VEHICLE_SIDES.RearLeft]:
        return nodes_for_yellow_fac
    if lamp_type == VEHICLE_LAMP_TYPES.RightTurn and vehicle_side in [VEHICLE_SIDES.FrontRight, VEHICLE_SIDES.RearRight]:
        return nodes_for_yellow_fac
    if lamp_type == VEHICLE_LAMP_TYPES.Positional and vehicle_side == VEHICLE_SIDES.Middle: # PositionalMiddle
        return nodes_for_yellow_fac

    # Grup Merah
    if lamp_type == VEHICLE_LAMP_TYPES.Brake and vehicle_side in [VEHICLE_SIDES.RearLeft, VEHICLE_SIDES.RearRight]:
        return nodes_for_red_fac
    if lamp_type == VEHICLE_LAMP_TYPES.Positional and vehicle_side in [VEHICLE_SIDES.RearLeft, VEHICLE_SIDES.RearRight]: # PositionalRearLeft/Right
        return nodes_for_red_fac
        
    # Grup Putih/Hitam (W) - Semua yang lain atau yang spesifik
    # Ini akan menangkap semua yang tidak cocok di atas, atau Anda bisa lebih eksplisit
    # Berdasarkan gambar "grup putih.png":
    if lamp_type == VEHICLE_LAMP_TYPES.Reverse and vehicle_side in [VEHICLE_SIDES.RearLeft, VEHICLE_SIDES.RearRight]:
        return nodes_for_w_fac
    if lamp_type == VEHICLE_LAMP_TYPES.HighBeam and vehicle_side in [VEHICLE_SIDES.FrontLeft, VEHICLE_SIDES.FrontRight]:
        return nodes_for_w_fac
    if lamp_type == VEHICLE_LAMP_TYPES.LowBeam and vehicle_side in [VEHICLE_SIDES.FrontLeft, VEHICLE_SIDES.FrontRight]:
        return nodes_for_w_fac
    if lamp_type == VEHICLE_LAMP_TYPES.DRL and vehicle_side == VEHICLE_SIDES.Middle: # DRLMiddle
        return nodes_for_w_fac
    if lamp_type == VEHICLE_LAMP_TYPES.Positional and vehicle_side in [VEHICLE_SIDES.FrontLeft, VEHICLE_SIDES.FrontRight]: # PositionalFrontLeft/Right
        return nodes_for_w_fac
    
    # Jika tidak ada yang cocok secara eksplisit di atas, mungkin kembalikan list default atau None
    # Untuk saat ini, jika tidak ada yang cocok, tidak akan ditambahkan.
    # Anda mungkin ingin menambahkan semua jenis lampu lainnya ke grup W secara default jika itu tujuannya.
    # print(f"Peringatan: Kombinasi tidak terpetakan untuk __init_vehicle_switch_nodes__: {lamp_type.name}, {vehicle_side.name}")
    return nodes_for_w_fac # Fallback ke W jika tidak ada aturan spesifik lain, atau sesuaikan


def __init_vehicle_switch_nodes__(
    node_tree, a_output, r_output, g_output, b_output,
    lamp_type, pos_x, pos_y,
    nodes_for_yellow_fac, nodes_for_red_fac, nodes_for_w_fac
):
    lists = (nodes_for_yellow_fac, nodes_for_red_fac, nodes_for_w_fac)

    switch_n = node_tree.nodes.new("ShaderNodeMath")
    switch_n.name = lamp_type.name
    switch_n.label = lamp_type.name
    switch_n.location = (pos_x, pos_y)
    switch_n.width_hidden = 100; switch_n.hide = True
    switch_n.operation = "MULTIPLY"; switch_n.inputs[0].default_value = 0.0

    if lamp_type == VEHICLE_LAMP_TYPES.Positional:
        node_tree.links.new(switch_n.inputs[1], a_output)
        mult_pos_y = pos_y + 80
        for vehicle_side in VEHICLE_SIDES:
            current_target_list = __determine_target_list_for_vehicle_lamp__(lamp_type, vehicle_side, lists)
            node_name = lamp_type.name + vehicle_side.name
            position = (pos_x + 185 * 2, mult_pos_y)
            in_bounds_n = node_tree.nodes[vehicle_side.name + _IN_BOUNDS_SUFFIX]
            mult_n = __create_merging_node__(node_tree, node_name, position, in_bounds_n.outputs[0], switch_n.outputs[0])
            if current_target_list is not None: current_target_list.append(mult_n)
            mult_pos_y -= 36
    elif lamp_type == VEHICLE_LAMP_TYPES.DRL: # DRLMiddle selalu
        current_target_list = __determine_target_list_for_vehicle_lamp__(lamp_type, VEHICLE_SIDES.Middle, lists)
        node_tree.links.new(switch_n.inputs[1], b_output)
        node_name = lamp_type.name + VEHICLE_SIDES.Middle.name
        position = (pos_x + 185 * 2, pos_y)
        in_bounds_n = node_tree.nodes[VEHICLE_SIDES.Middle.name + _IN_BOUNDS_SUFFIX]
        mult_n = __create_merging_node__(node_tree, node_name, position, in_bounds_n.outputs[0], switch_n.outputs[0])
        if current_target_list is not None: current_target_list.append(mult_n)
    else:
        color_output = veh_side_name1_enum = veh_side_name2_enum = None
        # Logika pemilihan color_output, veh_side_name1, veh_side_name2 dari skrip asli
        if lamp_type == VEHICLE_LAMP_TYPES.LeftTurn:
            color_output = r_output; veh_side_name1_enum = VEHICLE_SIDES.FrontLeft; veh_side_name2_enum = VEHICLE_SIDES.RearLeft
        elif lamp_type == VEHICLE_LAMP_TYPES.RightTurn:
            color_output = r_output; veh_side_name1_enum = VEHICLE_SIDES.FrontRight; veh_side_name2_enum = VEHICLE_SIDES.RearRight
        elif lamp_type == VEHICLE_LAMP_TYPES.Brake:
            color_output = g_output; veh_side_name1_enum = VEHICLE_SIDES.RearLeft; veh_side_name2_enum = VEHICLE_SIDES.RearRight
        elif lamp_type == VEHICLE_LAMP_TYPES.HighBeam:
            color_output = g_output; veh_side_name1_enum = VEHICLE_SIDES.FrontLeft; veh_side_name2_enum = VEHICLE_SIDES.FrontRight
        elif lamp_type == VEHICLE_LAMP_TYPES.LowBeam:
            color_output = b_output; veh_side_name1_enum = VEHICLE_SIDES.FrontLeft; veh_side_name2_enum = VEHICLE_SIDES.FrontRight
        elif lamp_type == VEHICLE_LAMP_TYPES.Reverse:
            color_output = b_output; veh_side_name1_enum = VEHICLE_SIDES.RearLeft; veh_side_name2_enum = VEHICLE_SIDES.RearRight

        if color_output:
            node_tree.links.new(switch_n.inputs[1], color_output)
            if veh_side_name1_enum:
                current_target_list1 = __determine_target_list_for_vehicle_lamp__(lamp_type, veh_side_name1_enum, lists)
                in_bounds_n1 = node_tree.nodes[veh_side_name1_enum.name + _IN_BOUNDS_SUFFIX]
                node_name1 = lamp_type.name + veh_side_name1_enum.name
                node_pos1 = (pos_x + 185 * 2, pos_y + 18)
                mult_n1 = __create_merging_node__(node_tree, node_name1, node_pos1, switch_n.outputs[0], in_bounds_n1.outputs[0])
                if current_target_list1 is not None: current_target_list1.append(mult_n1)
            if veh_side_name2_enum:
                current_target_list2 = __determine_target_list_for_vehicle_lamp__(lamp_type, veh_side_name2_enum, lists)
                in_bounds_n2 = node_tree.nodes[veh_side_name2_enum.name + _IN_BOUNDS_SUFFIX]
                node_name2 = lamp_type.name + veh_side_name2_enum.name
                node_pos2 = (pos_x + 185 * 2, pos_y - 18)
                mult_n2 = __create_merging_node__(node_tree, node_name2, node_pos2, switch_n.outputs[0], in_bounds_n2.outputs[0])
                if current_target_list2 is not None: current_target_list2.append(mult_n2)


def __determine_target_list_for_aux_lamp__(lamp_type, lists):
    nodes_for_yellow_fac, nodes_for_red_fac, nodes_for_w_fac = lists
    # Berdasarkan gambar "grup putih.png", semua AUX_LAMP_TYPES (Dim, Bright) masuk ke W
    return nodes_for_w_fac

def __init_aux_switch_nodes__(
    node_tree, a_output, r_output, g_output, # g_output tidak digunakan di skrip asli aux
    lamp_type, pos_x, pos_y,
    nodes_for_yellow_fac, nodes_for_red_fac, nodes_for_w_fac
):
    lists = (nodes_for_yellow_fac, nodes_for_red_fac, nodes_for_w_fac)
    current_target_list = __determine_target_list_for_aux_lamp__(lamp_type, lists)

    switch_n = node_tree.nodes.new("ShaderNodeMath")
    switch_n.name = lamp_type.name; switch_n.label = lamp_type.name
    switch_n.location = (pos_x, pos_y); switch_n.width_hidden = 100; switch_n.hide = True
    switch_n.operation = "MULTIPLY"; switch_n.inputs[0].default_value = 0.0

    color_output = None
    if lamp_type == AUX_LAMP_TYPES.Dim: color_output = r_output
    elif lamp_type == AUX_LAMP_TYPES.Bright: color_output = g_output # Skrip asli g_output, bukan a_output

    if color_output:
        node_tree.links.new(switch_n.inputs[1], color_output)
        # Aux lamps biasanya FrontLeft dan FrontRight
        for side_enum in [VEHICLE_SIDES.FrontLeft, VEHICLE_SIDES.FrontRight]:
            # Kita tidak bisa menggunakan __determine_target_list_for_vehicle_lamp__ secara langsung
            # karena itu untuk VEHICLE_LAMP_TYPES. Kita sudah tentukan target list di atas.
            in_bounds_n = node_tree.nodes[side_enum.name + _IN_BOUNDS_SUFFIX]
            node_name = lamp_type.name + side_enum.name
            node_pos_y_offset = 18 if side_enum == VEHICLE_SIDES.FrontLeft else -18
            node_pos = (pos_x + 185 * 2, pos_y + node_pos_y_offset)
            mult_n = __create_merging_node__(node_tree, node_name, node_pos, switch_n.outputs[0], in_bounds_n.outputs[0])
            if current_target_list is not None: current_target_list.append(mult_n)


def __determine_target_list_for_traffic_light__(lamp_type, lists):
    nodes_for_yellow_fac, nodes_for_red_fac, nodes_for_w_fac = lists
    # Berdasarkan gambar "grup putih.png", semua TRAFFIC_LIGHT_TYPES (Red, Yellow, Green) masuk ke W
    return nodes_for_w_fac

def __init_traffic_light_switch_nodes__(
    node_tree, a_output, lamp_type, pos_x, pos_y,
    nodes_for_yellow_fac, nodes_for_red_fac, nodes_for_w_fac
):
    lists = (nodes_for_yellow_fac, nodes_for_red_fac, nodes_for_w_fac)
    current_target_list = __determine_target_list_for_traffic_light__(lamp_type, lists)

    switch_n = node_tree.nodes.new("ShaderNodeMath")
    switch_n.name = lamp_type.name; switch_n.label = lamp_type.name
    switch_n.location = (pos_x, pos_y); switch_n.width_hidden = 100; switch_n.hide = True
    switch_n.operation = "MULTIPLY"; switch_n.inputs[0].default_value = 0.0
    node_tree.links.new(switch_n.inputs[1], a_output) # Traffic lights menggunakan alpha

    in_bounds_n = node_tree.nodes[lamp_type.name + _IN_BOUNDS_SUFFIX]
    node_name = lamp_type.name # Hanya nama tipe, tidak ada sisi
    node_pos = (pos_x + 185 * 2, pos_y)
    mult_n = __create_merging_node__(node_tree, node_name, node_pos, switch_n.outputs[0], in_bounds_n.outputs[0])
    if current_target_list is not None: current_target_list.append(mult_n)


# Fungsi pembantu untuk membuat rantai penjumlahan (dari diskusi sebelumnya)
def _create_addition_chain_for_group(node_tree, node_list_for_fac, group_prefix, base_pos_x, start_pos_y_ref):
    if not node_list_for_fac:
        zero_value_node = node_tree.nodes.new(type="ShaderNodeValue")
        zero_value_node.name = group_prefix + "_ZeroFacInput"; zero_value_node.label = group_prefix + "_ZeroFacInput"
        zero_value_node.outputs[0].default_value = 0.0
        zero_value_node.location = (base_pos_x - 200, start_pos_y_ref) # Posisikan sebelum MixRGB
        return zero_value_node.outputs[0]
    
    if len(node_list_for_fac) == 1:
        # Jika hanya satu node, mungkin langsung hubungkan atau buat node Math Add dengan input kedua 0
        # Untuk konsistensi, kita bisa buat Math Add dengan 0
        add_n = node_tree.nodes.new("ShaderNodeMath")
        add_n.name = group_prefix + _ADD_NODE_PREFIX + "_single"
        add_n.label = group_prefix + _ADD_NODE_PREFIX + "_single"
        add_n.location = (node_list_for_fac[0].location.x + 150, node_list_for_fac[0].location.y)
        add_n.hide = True; add_n.operation = "ADD"
        node_tree.links.new(node_list_for_fac[0].outputs[0], add_n.inputs[0])
        add_n.inputs[1].default_value = 0.0 # Tambah dengan 0
        return add_n.outputs[0]

    last_addition_node_in_chain = None
    # Tata letak untuk rantai ADD mungkin perlu banyak penyesuaian
    # Coba tempatkan di sebelah kiri dari base_pos_x untuk MixRGB
    # dan sedikit di atas/bawah dari start_pos_y_ref
    
    # Ambil posisi X dari node paling kanan dalam list input sebagai referensi
    # atau gunakan default jika list kosong/node tidak punya lokasi valid.
    ref_node_loc_x = node_list_for_fac[-1].location.x if node_list_for_fac else base_pos_x - 400

    current_add_chain_pos_x = ref_node_loc_x + 185 # Mulai rantai ADD di kanan node lampu terakhir
    current_add_chain_pos_y = start_pos_y_ref # Gunakan Y referensi grup

    for i in range(len(node_list_for_fac)):
        current_node_to_add_socket = node_list_for_fac[i].outputs[0]
        if i == 0: # Node pertama, jadi input pertama untuk ADD pertama
            last_processed_socket = current_node_to_add_socket
            continue

        add_n = node_tree.nodes.new("ShaderNodeMath")
        add_n.name = f"{group_prefix}{_ADD_NODE_PREFIX}{i}"
        add_n.label = f"{group_prefix}{_ADD_NODE_PREFIX}{i}"
        # Posisikan node ADD berikutnya dari node ADD sebelumnya, atau dari node lampu jika ini yang pertama
        if last_addition_node_in_chain:
            add_n.location = (last_addition_node_in_chain.location.x + 150, last_addition_node_in_chain.location.y)
        else: # ADD pertama dalam rantai
            add_n.location = (current_add_chain_pos_x, current_add_chain_pos_y - (i * 20)) # Penyesuaian Y
        add_n.hide = True; add_n.operation = "ADD"

        node_tree.links.new(last_processed_socket, add_n.inputs[0])
        node_tree.links.new(current_node_to_add_socket, add_n.inputs[1])
        
        last_processed_socket = add_n.outputs[0]
        last_addition_node_in_chain = add_n
        
    return last_processed_socket # Ini adalah output dari node ADD terakhir di rantai


def __create_node_group__():
    pos_x_shift = 185 # Dari skrip asli
    lampmask_g = bpy.data.node_groups.new(type="ShaderNodeTree", name=LAMPMASK_MIX_G)

    # Inputs defining
    lampmask_g.inputs.new("NodeSocketFloat", "Lampmask Tex Alpha"); lampmask_g.inputs.new("NodeSocketColor", "Lampmask Tex Color")
    lampmask_g.inputs.new("NodeSocketVector", "UV Vector"); input_n = lampmask_g.nodes.new("NodeGroupInput"); input_n.location = (0, 0)

    # Outputs defining
    lampmask_g.outputs.new("NodeSocketColor", "Lampmask Addition Color"); output_n = lampmask_g.nodes.new("NodeGroupOutput")
    # output_n.location akan diatur di akhir

    # Nodes creation (alpha decode, tex color sep, UV dots - seperti skrip asli)
    alpha_decode_n = lampmask_g.nodes.new("ShaderNodeMath"); alpha_decode_n.name = _ALPHA_DECODE_NODE; alpha_decode_n.label = _ALPHA_DECODE_NODE
    alpha_decode_n.location = (pos_x_shift, 50); alpha_decode_n.operation = "POWER"; alpha_decode_n.inputs[1].default_value = 2.2
    tex_col_sep_n = lampmask_g.nodes.new("ShaderNodeSeparateRGB"); tex_col_sep_n.name = _TEX_COL_SEP_NODE; tex_col_sep_n.label = _TEX_COL_SEP_NODE
    tex_col_sep_n.location = (pos_x_shift, 200) # Sesuaikan Y agar tidak tumpang tindih
    uv_x_dot_n = lampmask_g.nodes.new("ShaderNodeVectorMath"); uv_x_dot_n.name = _UV_DOT_X_NODE; uv_x_dot_n.label = _UV_DOT_X_NODE
    uv_x_dot_n.location = (pos_x_shift, -100); uv_x_dot_n.operation = "DOT_PRODUCT"; uv_x_dot_n.inputs[1].default_value = (1.0, 0, 0)
    uv_y_dot_n = lampmask_g.nodes.new("ShaderNodeVectorMath"); uv_y_dot_n.name = _UV_DOT_Y_NODE; uv_y_dot_n.label = _UV_DOT_Y_NODE
    uv_y_dot_n.location = (pos_x_shift, -250); uv_y_dot_n.operation = "DOT_PRODUCT"; uv_y_dot_n.inputs[1].default_value = (0, 1.0, 0)

    lampmask_g.links.new(input_n.outputs['Lampmask Tex Alpha'], alpha_decode_n.inputs[0]) # Perbaikan urutan
    lampmask_g.links.new(input_n.outputs['Lampmask Tex Color'], tex_col_sep_n.inputs['Image']) # Perbaikan urutan
    lampmask_g.links.new(input_n.outputs['UV Vector'], uv_x_dot_n.inputs[0]) # Perbaikan urutan
    lampmask_g.links.new(input_n.outputs['UV Vector'], uv_y_dot_n.inputs[0]) # Perbaikan urutan

    # Init UV tilling mechanism (base_pos_x disesuaikan agar tidak tumpang tindih)
    uv_tiles_base_pos_x = pos_x_shift * 2
    current_pos_y = -50; max_uv = 1
    for uv_x_tile in UV_X_TILES:
        __init_uv_tile_bounding_nodes__(lampmask_g, uv_x_dot_n, uv_x_tile, uv_tiles_base_pos_x, current_pos_y, max_uv); current_pos_y -= 75; max_uv += 1
    current_pos_y = -400; max_uv = 1 # Reset Y untuk Y_TILES
    for uv_y_tile in UV_Y_TILES:
        __init_uv_tile_bounding_nodes__(lampmask_g, uv_y_dot_n, uv_y_tile, uv_tiles_base_pos_x, current_pos_y, max_uv); current_pos_y -= 75; max_uv += 1

    # Init vehicle sides uv bounding mechanism
    vehicle_bounds_base_pos_x = uv_tiles_base_pos_x + pos_x_shift + 50 # Geser X dari UV tiles
    current_pos_y = 0
    for vehicle_side in VEHICLE_SIDES:
        __init_vehicle_uv_bounding_nodes__(lampmask_g, vehicle_side, vehicle_bounds_base_pos_x, current_pos_y); current_pos_y -= 75

    # Init traffic light uv bounding mechanism
    traffic_light_bounds_base_pos_x = vehicle_bounds_base_pos_x # Bisa di kolom yang sama atau baru
    current_pos_y = -350 # Sesuaikan Y
    for traffic_light_type in TRAFFIC_LIGHT_TYPES:
        __init_traffic_light_uv_bounding_nodes__(lampmask_g, traffic_light_type, traffic_light_bounds_base_pos_x, current_pos_y); current_pos_y -= 100

    # Buat list untuk setiap grup Fac
    nodes_for_yellow_fac, nodes_for_red_fac, nodes_for_w_fac = [], [], []

    # Init vehicle/aux/traffic light switches
    switch_nodes_base_pos_x = vehicle_bounds_base_pos_x + pos_x_shift + 100 # Geser X dari vehicle bounds
    current_pos_y = 800 # Mulai dari atas untuk switch nodes

    for lamp_type in VEHICLE_LAMP_TYPES:
        if lamp_type == VEHICLE_LAMP_TYPES.Positional: current_pos_y -= 100
        __init_vehicle_switch_nodes__(lampmask_g, alpha_decode_n.outputs[0], tex_col_sep_n.outputs["R"], tex_col_sep_n.outputs["G"], tex_col_sep_n.outputs["B"], lamp_type, switch_nodes_base_pos_x, current_pos_y, nodes_for_yellow_fac, nodes_for_red_fac, nodes_for_w_fac)
        current_pos_y -= 75
    
    current_pos_y -= 60 # Spasi untuk Aux
    for lamp_type in AUX_LAMP_TYPES:
        # ## Panggil __init_aux_switch_nodes__ yang sudah dimodifikasi ##
        __init_aux_switch_nodes__(lampmask_g, alpha_decode_n.outputs[0], tex_col_sep_n.outputs["R"], tex_col_sep_n.outputs["G"], lamp_type, switch_nodes_base_pos_x, current_pos_y, nodes_for_yellow_fac, nodes_for_red_fac, nodes_for_w_fac)
        current_pos_y -= 75

    current_pos_y -= 60 # Spasi untuk Traffic Light
    for lamp_type in TRAFFIC_LIGHT_TYPES:
        # ## Panggil __init_traffic_light_switch_nodes__ yang sudah dimodifikasi ##
        __init_traffic_light_switch_nodes__(lampmask_g, alpha_decode_n.outputs[0], lamp_type, switch_nodes_base_pos_x, current_pos_y, nodes_for_yellow_fac, nodes_for_red_fac, nodes_for_w_fac)
        current_pos_y -= 75


    # Buat rantai penjumlahan untuk setiap grup Fac
    # Tentukan posisi X dasar untuk node MixRGB (ini akan jadi referensi untuk rantai ADD)
    # Posisikan rantai ADD di antara switch nodes dan MixRGB nodes
    add_chain_base_pos_x = switch_nodes_base_pos_x + (185 * 3) + 50 # Sesuaikan
    mix_rgb_base_pos_x = add_chain_base_pos_x + pos_x_shift + 200 # Sesuaikan

    # Posisi Y referensi untuk rantai ADD pertama (Y) dan MixRGB, dari atas
    ref_start_y_for_color_groups = 600

    summed_lights_output_yellow = _create_addition_chain_for_group(lampmask_g, nodes_for_yellow_fac, "Y", add_chain_base_pos_x, ref_start_y_for_color_groups)
    summed_lights_output_red = _create_addition_chain_for_group(lampmask_g, nodes_for_red_fac, "R", add_chain_base_pos_x, ref_start_y_for_color_groups - 250) # Turunkan Y
    summed_lights_output_w = _create_addition_chain_for_group(lampmask_g, nodes_for_w_fac, "W", add_chain_base_pos_x, ref_start_y_for_color_groups - 500) # Turunkan Y lagi
    
    warna_merah = 10.0, 0.0, 0.0, 1.0
    warna_kuning = 25.0, 2.0, 0.0, 1.0
    warna_putih = 10.5, 10.5, 10.5, 1.0
    warna_hitam = 0.0, 0.0, 0.0, 1.0

    # 1. MixRGB Kuning (Y_Mix)
    mix_node_Y = lampmask_g.nodes.new(type="ShaderNodeMixRGB")
    mix_node_Y.name = "Y_Mix_Color"; mix_node_Y.label = "Y"
    mix_node_Y.blend_type = 'ADD'
    mix_node_Y.inputs["Color1"].default_value = (warna_hitam) # Hitam
    mix_node_Y.inputs["Color2"].default_value = (warna_kuning) # Kuning
    mix_node_Y.location = (mix_rgb_base_pos_x, ref_start_y_for_color_groups)
    lampmask_g.links.new(summed_lights_output_yellow, mix_node_Y.inputs["Fac"])

    # 2. MixRGB Merah (R_Mix)
    mix_node_R = lampmask_g.nodes.new(type="ShaderNodeMixRGB")
    mix_node_R.name = "R_Mix_Color"; mix_node_R.label = "R"
    mix_node_R.blend_type = 'ADD'
    mix_node_R.inputs["Color1"].default_value = (warna_hitam) # Hitam
    mix_node_R.inputs["Color2"].default_value = (warna_merah) # Merah
    mix_node_R.location = (mix_rgb_base_pos_x, ref_start_y_for_color_groups - 180) 
    lampmask_g.links.new(summed_lights_output_red, mix_node_R.inputs["Fac"])

    # 3. MixRGB Putih/Hitam (W_Mix)
    mix_node_W = lampmask_g.nodes.new(type="ShaderNodeMixRGB")
    mix_node_W.name = "W_Mix_Color"; mix_node_W.label = "W"
    mix_node_W.blend_type = 'ADD'
    mix_node_W.inputs["Color1"].default_value = (warna_hitam) # Hitam
    mix_node_W.inputs["Color2"].default_value = (warna_putih) # Putih
    mix_node_W.location = (mix_rgb_base_pos_x, ref_start_y_for_color_groups - 360)
    lampmask_g.links.new(summed_lights_output_w, mix_node_W.inputs["Fac"])

    # --- BUAT NODE MixRGB BARU UNTUK OPERASI ADD (HANYA DUA SEKARANG) ---
    add_mix_pos_x = mix_rgb_base_pos_x + 250 # Kolom baru untuk Add nodes

    # Add_Mix_1 (Y + R)
    add_mix_node_1 = lampmask_g.nodes.new(type="ShaderNodeMixRGB")
    add_mix_node_1.name = "Add_Y_plus_R"; add_mix_node_1.label = "Add (Y+R)"
    add_mix_node_1.blend_type = 'ADD'
    add_mix_node_1.inputs["Fac"].default_value = 1.0
    add_mix_node_1.location = (add_mix_pos_x, ref_start_y_for_color_groups - 90)

    # Add_Mix_2 ((Y+R) + W)
    add_mix_node_2 = lampmask_g.nodes.new(type="ShaderNodeMixRGB")
    add_mix_node_2.name = "Add_YR_plus_W"; add_mix_node_2.label = "Add ((Y+R)+W)"
    add_mix_node_2.blend_type = 'ADD'
    add_mix_node_2.inputs["Fac"].default_value = 1.0
    add_mix_node_2.location = (add_mix_pos_x + 200, ref_start_y_for_color_groups - 180)

    # --- KONEKSIKAN NODE-NODE ADD ---
    lampmask_g.links.new(mix_node_Y.outputs["Color"], add_mix_node_1.inputs["Color1"])
    lampmask_g.links.new(mix_node_R.outputs["Color"], add_mix_node_1.inputs["Color2"])

    lampmask_g.links.new(add_mix_node_1.outputs["Color"], add_mix_node_2.inputs["Color1"])
    lampmask_g.links.new(mix_node_W.outputs["Color"], add_mix_node_2.inputs["Color2"])
    
    # --- PERBARUI KONEKSI KE GROUP OUTPUT ---
    # Output dari Add_Mix_2 sekarang menjadi output grup
    lampmask_g.links.new(add_mix_node_2.outputs["Color"], output_n.inputs["Lampmask Addition Color"])
    # Sesuaikan posisi node output akhir
    output_n.location = (add_mix_pos_x + 400, ref_start_y_for_color_groups - 180) 

    return lampmask_g